# -*- coding: utf-8 -*-

from odoo import api, models, fields


class AdministratorMixinRule(models.AbstractModel):
    """Abstract model for administrator permission rules"""
    _name = 'administrator.mixin.rule'
    _description = 'Administrator Mixin Rule'

    is_admin = fields.Boolean(
        compute='_compute_is_admin',
        string="Is Admin",
        store=False
    )

    @api.depends_context('uid')
    def _compute_is_admin(self):
        """Compute if current user is admin"""
        has_admin = self.env.user.has_group('d_hr_administration.administration')
        for record in self:
            record.is_admin = has_admin

    can_edit_tax = fields.Boolean(
        compute='_compute_can_edit_tax',
        string="Can Edit Tax",
        store=False
    )

    @api.depends_context('uid')
    def _compute_can_edit_tax(self):
        """Compute if user can edit tax"""
        can_edit = self.env.user.has_group('d_hr_administration.edit_tax')
        for record in self:
            record.can_edit_tax = can_edit

    can_edit_discounts = fields.Boolean(
        compute='_compute_can_edit_discounts',
        string="Can Edit Discounts",
        store=False
    )

    @api.depends_context('uid')
    def _compute_can_edit_discounts(self):
        """Compute if user can edit discounts"""
        can_edit = self.env.user.has_group('d_hr_administration.edit_discounts')
        for record in self:
            record.can_edit_discounts = can_edit

    can_edit_price = fields.Boolean(
        compute='_compute_can_edit_price',
        string="Can Edit Price",
        store=False
    )

    @api.depends_context('uid')
    def _compute_can_edit_price(self):
        """Compute if user can edit price"""
        can_edit = self.env.user.has_group('d_hr_administration.edit_sale_price')
        for record in self:
            record.can_edit_price = can_edit

    can_edit_account = fields.Boolean(
        compute='_compute_can_edit_account',
        string="Can Edit Account",
        store=False
    )

    @api.depends_context('uid')
    def _compute_can_edit_account(self):
        """Compute if user can edit account"""
        can_edit = self.env.user.has_group('d_hr_administration.edit_account')
        for record in self:
            record.can_edit_account = can_edit

    can_edit_quantity = fields.Boolean(
        compute='_compute_can_edit_quantity',
        string="Can Edit Quantity",
        store=False
    )

    @api.depends_context('uid')
    def _compute_can_edit_quantity(self):
        """Compute if user can edit quantity"""
        can_edit = self.env.user.has_group('d_hr_administration.edit_quantity')
        for record in self:
            record.can_edit_quantity = can_edit

    can_edit_product_desc = fields.Boolean(
        compute='_compute_can_edit_product_desc',
        string="Can Edit Product Description",
        store=False
    )

    @api.depends_context('uid')
    def _compute_can_edit_product_desc(self):
        """Compute if user can edit product description"""
        can_edit = self.env.user.has_group('d_hr_administration.edit_product_desc')
        for record in self:
            record.can_edit_product_desc = can_edit

    can_edit_product_id = fields.Boolean(
        compute='_compute_can_edit_product_id',
        string="Can Edit Product",
        store=False
    )

    @api.depends_context('uid')
    def _compute_can_edit_product_id(self):
        """Compute if user can edit product"""
        can_edit = self.env.user.has_group('d_hr_administration.edit_product_id')
        for record in self:
            record.can_edit_product_id = can_edit

    can_cancel_invoice = fields.Boolean(
        compute='_compute_can_cancel_invoice',
        string="Can Cancel Invoice",
        store=False
    )

    @api.depends_context('uid')
    def _compute_can_cancel_invoice(self):
        """Compute if user can cancel invoice"""
        can_cancel = self.env.user.has_group('d_hr_administration.cancel_invoice')
        for record in self:
            record.can_cancel_invoice = can_cancel

    can_create_refund_invoice = fields.Boolean(
        compute='_compute_can_create_refund_invoice',
        string="Can Create Refund Invoice",
        store=False
    )

    @api.depends_context('uid')
    def _compute_can_create_refund_invoice(self):
        """Compute if user can create refund invoice"""
        can_create = self.env.user.has_group('d_hr_administration.create_refund_invoice')
        for record in self:
            record.can_create_refund_invoice = can_create
