/** @odoo-module **/


import { registry } from "@web/core/registry";
import { Component, useEffect, useRef, useState, onWillStart, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class FieldDigitalSignature extends Component {
    static template = "web_digital_sign.FieldDigitalSignature";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.signatureRef = useRef("signature");
        this.jSignatureLoaded = false;
        this.state = useState({
            signatureUrl: null,
            isEmpty: true,
            isLoading: true,
        });
        console.log("DigitalSignature props:", this.props);


        this.signOptions = {
            'decor-color': '#D1D0CE',
            'color': '#000',
            'background-color': '#fff',
            'height': '150',
            'width': '550'
        };

        onWillStart(async () => {
            await this.loadJSignature();
        });

        onMounted(() => {
            if (this.jSignatureLoaded) {
                this.initSignature();
                if (this.fieldValue) {
                    this.loadSignature();
                }
            }
        });

        useEffect(() => {
            if (this.jSignatureLoaded) {
                this.initSignature();
            }
        }, () => [this.isReadonly, this.jSignatureLoaded]);

        useEffect(() => {
            if (this.jSignatureLoaded && this.fieldValue) {
                this.loadSignature();
            }
        }, () => [this.fieldValue, this.jSignatureLoaded]);
    }

    get fieldName() {
        return this.props.name;
    }

    get fieldValue() {
        return this.props.record.data[this.fieldName];
    }

    get isReadonly() {
        return this.props.readonly || false;
    }


    async loadJSignature() {
        if (this.jSignatureLoaded) return;

        try {
            // Asegurarse de que jQuery esté disponible globalmente
            if (typeof window.$ === 'undefined' && typeof $ !== 'undefined') {
                window.$ = $;
                window.jQuery = $;
            }

            await loadJS("/web_digital_sign/static/lib/jSignature/jSignatureCustom.js");
            this.jSignatureLoaded = true;
            this.state.isLoading = false;
        } catch (error) {
            console.error("Error loading jSignature:", error);
            this.state.isLoading = false;
        }
    }

    initSignature() {
        if (!this.signatureRef.el || !this.jSignatureLoaded) return;

        const $signature = $(this.signatureRef.el);
        $signature.empty();

        if (!this.isReadonly) {
            try {
                $signature.jSignature("init", this.signOptions);
                $signature.attr({
                    "tabindex": "0",
                    'height': "100"
                });
                this.emptySign = $signature.jSignature("getData", 'image');
            } catch (error) {
                console.error("Error initializing signature:", error);
            }
        }
    }

    async loadSignature() {
        const value = this.fieldValue;
        if (!value) return;

        if (this.isReadonly) {
            this.state.signatureUrl = 'data:image/png;base64,' + value;
        } else {
            const $signature = $(this.signatureRef.el);
            if (!$signature.length) return;

            try {
                const resId = this.props.record && this.props.record.resId;
                if (!resId) return;

                const data = await this.orm.read(
                    this.props.record.resModel,
                    [resId],
                    [this.fieldName]
                );
                if (data && data[0]) {
                    const fieldValue = data[0][this.fieldName];
                    if (fieldValue) {
                        $signature.jSignature("clear");
                        $signature.jSignature("setData", 'data:image/png;base64,' + fieldValue);
                        this.state.isEmpty = false;
                    }
                }
            } catch (error) {
                console.error("Error loading signature data:", error);
            }
        }
    }

    onClearSign() {
        if (!this.jSignatureLoaded) return;

        const $signature = $(this.signatureRef.el);
        $signature.find("canvas").remove();
        $signature.attr("tabindex", "0");

        try {
            $signature.jSignature(this.signOptions);
            $signature.focus();
            this.state.isEmpty = true;
            this.emptySign = $signature.jSignature("getData", 'image');
            if (this.props.record && this.props.record.update) {
                this.props.record.update({ [this.fieldName]: false });
            }
        } catch (error) {
            console.error("Error clearing signature:", error);
        }
    }

    onSaveSign() {
        if (!this.jSignatureLoaded) return;

        const $signature = $(this.signatureRef.el);
        try {
            const signature = $signature.jSignature("getData", 'image');
            const isEmpty = signature ? this.emptySign[1] === signature[1] : false;

            if (!isEmpty && signature && signature[1]) {
                this.state.isEmpty = false;
                if (this.props.record && this.props.record.update) {
                    this.props.record.update({ [this.fieldName]: signature[1] });
                }
            }
        } catch (error) {
            console.error("Error saving signature:", error);
        }
    }

    get placeholder() {
        return "/web/static/img/placeholder.png";
    }

    get imageUrl() {
        const value = this.fieldValue;
        if (!value) {
            return this.placeholder;
        }
        if (this.state.signatureUrl) {
            return this.state.signatureUrl;
        }
        return 'data:image/png;base64,' + value;
    }
}

// Registrar en ambas categorías para compatibilidad con Odoo 18
registry.category("fields").add("digital_signature", {
    component: FieldDigitalSignature,
    supportedTypes: ["binary"],
});

registry.category("view_widgets").add("digital_signature", {
    component: FieldDigitalSignature,
});
