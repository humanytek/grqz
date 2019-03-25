MRP II
======

This module allows to know the real stock of materials (from the bill of materials) to sell a product.

Usage
=====

- Go to **Production> Planning> MRP II**

|

.. figure:: ../mrp_ii/static/src/img/menu.png
   :align: center
   :width: 400pt


1. It must select the product to be sold, by default the bill of materials of the selected product is associated.
2. The amount of the product to be sold must be indicated.
3. The location of the stock is the default location. (*)
4. Press the **Calculate** button.

|

.. figure:: ../mrp_ii/static/src/img/steps.png
   :align: center
   :width: 400pt

The following is shown for each material in the bill of materials:

- Quantity (necessary to manufacture the selected product).
- Total products (physical quantity of each material).
- Total reserved products (reserved quantity of each material).
- Available products (Total products - Total products reserved).
- Total incoming products (materials in transit).
- Total committed products.
- Incoming products available (Total incoming products - Total products committed).

|

.. figure:: ../mrp_ii/static/src/img/result.png
   :align: center
   :width: 400pt

For each material, the sales and purchase information associated with said material are shown:

|

.. figure:: ../mrp_ii/static/src/img/saleinformation.png
   :align: center
   :width: 400pt

|

.. figure:: ../mrp_ii/static/src/img/salepurchaseinfo.png
   :align: center
   :width: 400pt

(*)
The default location must have the field **is default location?** checked.

|

.. figure:: ../mrp_ii/static/src/img/stocklocation.png
   :align: center
   :width: 400pt

Credits
=======

Contributors
------------
* Leandro Pacheco <leandro@vauxoo.com>
* José Morales <jose@vauxoo.com>
* Edilianny Sánchez <esanchez@vauxoo.com>
* Germana Oliveira <germana@vauxoo.com>

Do not contact contributors directly about support or help with technical issues.

Maintainer
----------

.. image:: https://s3.amazonaws.com/s3.vauxoo.com/description_logo.png
   :alt: Vauxoo
   :target: https://vauxoo.com
