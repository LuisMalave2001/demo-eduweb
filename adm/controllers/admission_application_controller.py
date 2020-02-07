# -*- coding: utf-8 -*-
from odoo import http
from datetime import datetime
import base64


def get_parameters():
    return http.request.httprequest.args


def post_parameters():
    return http.request.httprequest.form


class Admission(http.Controller):

    def get_partner(self):
        return http.request.env["res.users"].browse([http.request.session.uid]).partner_id
    
    @http.route("/admission/application", auth="public", methods=["GET"], website=True)
    def admission_web(self, **params):
        contact_id = self.get_partner()
        application_status_ids = http.request.env["adm.application.status"].browse(http.request.env["adm.application.status"].search([])).ids
        contact_time_ids = http.request.env["adm.contact_time"].browse(http.request.env["adm.contact_time"].search([])).ids
        degree_program_ids = http.request.env["adm.degree_program"].browse(http.request.env["adm.degree_program"].search([])).ids
        
        language_ids = http.request.env['adm.languages'].browse(http.request.env['adm.languages'].search([]))
        language_level_ids = http.request.env['adm.languages.level'].browse(http.request.env['adm.languages.level'].search([]))
        
        response = http.request.render('adm.template_admission_application', {
            'contact_id': contact_id,
            'application_status_ids': application_status_ids,
            'language_ids': language_ids.ids,
            'language_level_ids': language_level_ids.ids,
            'contact_time_ids': contact_time_ids,
            'degree_program_ids': degree_program_ids,
        })
        return response
    
    @http.route("/admission/message", auth="public", methods=["POST"], website=True, csrf=False)
    def send_message(self, **params):
        
        print("Params: {}".format(params))
        contact_id = self.get_partner()
        
        upload_file = params["file_upload"]
        message_body = params["message_body"]
        
        message_body=message_body.replace("\n","<br />\n")
        
        MessageEnv = http.request.env["mail.message"]
        message_id = MessageEnv.create({
            'date': datetime.today(),
            'email_from': '"{}" <{}>'.format(contact_id.name, contact_id.email),
            'author_id': contact_id.id,
            'record_name': "",
            "model": "adm.application",
            "res_id": contact_id.uni_application_id.id,
            "message_type": "comment",
            "subtype_id": 1,
            "body": "<p>{}</p>".format(message_body),
        })
        
        AttachmentEnv = http.request.env["ir.attachment"]
        
        if upload_file:
            file_id = AttachmentEnv.sudo().create({
                'name': upload_file.filename,
                'datas_fname': upload_file.filename,
                'res_name': upload_file.filename,
                'type': 'binary',   
                'res_model': 'adm.application',
                'res_id': contact_id.uni_application_id,
                'datas': base64.b64encode(upload_file.read()),
            })
        
        return http.request.redirect('/admission/application')
        
        #===============================================================================================================
        # return "Ok"
        #===============================================================================================================

    @http.route("/admission/application", auth="public", methods=["POST"], website=True, csrf=False)
    def add_admission(self, **params):
        if "txtMiddleName" not in params:
            params["txtMiddleName"] = ""

        full_name = "{}, {}{}".format(params["txtLastName"], "" if not params["txtMiddleName"] else params["txtMiddleName"] + " ",
                                      params["txtFirstName"])

        new_parent_dict = {'name': full_name,
                           'first_name': params["txtFirstName"],
                           'middle_name': params["txtMiddleName"],
                           'last_name': params["txtLastName"],
                           'salutation': params["txtSalutation"],
                           'email': params["txtEmail"],
                           'mobile': params["txtCellPhone"],
                           'phone': params["txtHomePhone"],
                           'street': params["txtStreetAddress"],
                           # 'country': params["selCountry"],
                           'zip': params["txtZip"]}

        if params["selState"] != "-1":
            new_parent_dict["state"] = params["selState"]

        partners = http.request.env['res.partner']
        id_parent = partners.create(new_parent_dict)

        # Create a lead
        print("id_parent: {}".format(id_parent.id))
        id_lead = http.request.env['crm.lead'].create(
            {"name": "test",
             "partner_id": id_parent.id})

        # Create students
        id_students = list()
        students_total = int(params["studentsCount"])

        first_name_list = post_parameters().getlist("txtStudentFirstName")
        last_name_list = post_parameters().getlist("txtStudentLastName")
        middle_name_list = post_parameters().getlist("txtStudentMiddleName")
        birthday_list = post_parameters().getlist("txtStudentBirthday")
        grade_level_list = post_parameters().getlist("selStudentGradeLevel")
        school_year_list = post_parameters().getlist("selStudentSchoolYear")
        current_school_list = post_parameters().getlist("txtStudentCurrentSchool")
        gender_list = post_parameters().getlist("selStudentGender")
        InquiryEnv = http.request.env["admission.inquiry"]

        for index_student in range(students_total):
            # print("{} -> {}".format(first_name_list, index_student))
            first_name = first_name_list[index_student]
            middle_name = middle_name_list[index_student]
            last_name = last_name_list[index_student]
            birthday = birthday_list[index_student]
            grade_level = grade_level_list[index_student]
            school_year = school_year_list[index_student]
            current_school = current_school_list[index_student]
            gender = gender_list[index_student]
            
            full_name_student = "{}, {}{}".format(last_name, "" if not middle_name else middle_name + " ", first_name)

            id_student = InquiryEnv.create({
                'first_name': first_name,
                'middle_name': middle_name,
                'last_name': last_name,
                'gender':  gender,
                'birthday': birthday,
                'email': params["txtEmail"],
                'school_year': school_year,
                'grade_level': grade_level,
                'current_school': current_school,
                'responsible_id': id_parent.id
            })
            id_students.append(id_student)
        
        return http.request.redirect('/admission/application')
