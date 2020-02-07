# -*- coding: utf-8 -*-

from odoo import models, fields


class AdmissionLanguages(models.Model):
    _name = "adm.languages"
    
    name = fields.Char("Name", required=True)
    
class AdmissionLanguageLevels(models.Model):
    _name = "adm.languages.level"
    
    name = fields.Char("Name", required=True)
    