'''
Created on Feb 1, 2020

@author: LuisMora
'''
from odoo import models, fields

class ResPartnerExtended(models.Model):
    _inherit = ["res.partner"]
    
    application_id = fields.Many2one("adm.application", string="Application")
    inquiry_id = fields.Many2one("adm.inquiry", string="Inquiry")
    is_in_application = fields.Boolean("Is in Application?")
