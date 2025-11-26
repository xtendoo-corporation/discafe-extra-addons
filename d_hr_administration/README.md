# D & HR Administrator - Odoo 18

## Descripción
Módulo de administración para Discafé y Huelva Regalos actualizado para Odoo 18.

Este módulo proporciona controles de administración y restricciones de permisos para la gestión de ventas, compras y facturación.

## Versión
- **Versión**: 18.0.1.0.0
- **Compatible con**: Odoo 18.0

## Cambios principales en la migración a Odoo 18

### 1. Modelos actualizados
- Todos los modelos heredan correctamente de `administrator.mixin.rule` como un `AbstractModel`
- `account.invoice` ha sido completamente reemplazado por `account.move`
- Actualización de métodos deprecados:
  - `action_invoice_cancel()` → `action_cancel()`
  - `cancel()` → `action_cancel()`

### 2. Campos computados mejorados
- Uso de `@api.depends_context('uid')` para campos que dependen del usuario actual
- Métodos de cómputo renombrados siguiendo convenciones de Odoo 18:
  - `_compute_*` en lugar de métodos personalizados
- Eliminación de métodos `default_get` redundantes

### 3. Vistas XML actualizadas
- Cambio de `invisible="1"` a `column_invisible="True"` en vistas tree
- IDs de vistas únicos actualizados para evitar conflictos
- Atributos `readonly` mejorados usando la nueva sintaxis sin `attrs`
- Adición de `options="{'no_create': True}"` en campos many2one para mayor control

### 4. Seguridad mejorada
- Validaciones de permisos actualizadas
- Grupos de seguridad mantenidos y compatibles con Odoo 18

## Funcionalidades principales

### Control de permisos administrativos
- **Grupo Administración**: Control total sobre el sistema
- **Restricciones de edición**: 
  - Precios
  - Descuentos
  - Impuestos
  - Cuentas contables
  - Cantidades
  - Productos
  - Descripciones

### Módulos afectados
- **Ventas**: Restricciones en pedidos de venta y líneas
- **Facturación**: Control sobre creación y modificación de facturas
- **Pagos**: Restricciones de fecha y cancelación
- **Productos**: Control sobre edición de productos y plantillas

## Dependencias
- base
- purchase
- sale
- product
- sale_margin
- account
- account_invoice_margin
- xtendoo_partner_delivery_zone

## Instalación

1. Colocar el módulo en la carpeta de addons de Odoo 18
2. Actualizar la lista de aplicaciones
3. Instalar el módulo "D & HR Administrator"
4. Configurar los grupos de usuarios según necesidades

## Grupos de seguridad incluidos

- `d_hr_administration.administration` - Administrador total
- `d_hr_administration.show_cost_price` - Ver precio de coste
- `d_hr_administration.show_margins` - Ver márgenes
- `d_hr_administration.edit_tax` - Editar impuestos
- `d_hr_administration.edit_discounts` - Editar descuentos
- `d_hr_administration.edit_sale_price` - Editar precio de venta
- `d_hr_administration.edit_account` - Editar cuentas contables
- `d_hr_administration.edit_quantity` - Editar cantidades
- `d_hr_administration.edit_product_desc` - Editar descripciones de producto
- `d_hr_administration.edit_product_id` - Editar productos
- `d_hr_administration.cancel_invoice` - Cancelar facturas
- `d_hr_administration.create_refund_invoice` - Crear facturas rectificativas

## Notas de migración

Esta versión ha sido completamente actualizada para ser compatible con Odoo 18, manteniendo toda la funcionalidad original pero adaptada a las nuevas APIs y convenciones de la versión 18.

## Autor
- **DDL**
- **Company**: Xtendoo
- **Website**: https://xtendoo.es/

## Licencia
AGPL-3
