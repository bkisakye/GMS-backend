# management/commands/populate_default_questions.py
from django.core.management.base import BaseCommand
from grants_management.models import DefaultApplicationQuestion, Section, SubSection


class Command(BaseCommand):
    help = "Populate default application questions with sections and subsections"

    def handle(self, *args, **kwargs):
        # Define sections
        sections = [
            {"title": "General Information"},
            {"title": "Proposed Areas of Work and Experience"},
            {"title": "Signature Page"},
        ]

        # Create or get sections
        section_objects = {
            sec["title"]: Section.objects.get_or_create(**sec)[0] for sec in sections
        }

        # Define subsections with their respective sections
        subsections = [
            {
                "title": "Justification for proposed partnership",
                "section": section_objects["General Information"],
            },
            {
                "title": "Problem and Proposed intervention(s)",
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "title": "Justification for proposed intervention(s)",
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "title": "Budget and Duration",
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "title": "Geographic Coverage",
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "title": "Project Stakeholders and Beneficiaries",
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "title": "Conflict sensitivity",
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "title": "What are the risks and assumptions for the proposed work?",
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "title": "Anticipated partnerships",
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "title": "Non-Discrimination",
                "section": section_objects["Signature Page"],
            },
            {"title": "Anti-Corruption", "section": section_objects["Signature Page"]},
            {
                "title": "CheckList of Documents to attach to eOi",
                "section": section_objects["Signature Page"],
            },
            {"title": "Signature", "section": section_objects["Signature Page"]},
        ]

        # Create or get subsections
        subsection_objects = {
            subsec["title"]: SubSection.objects.get_or_create(**subsec)[0]
            for subsec in subsections
        }

        # Define questions
        questions = [
            {
                "text": "Why should Baylor-Uganda choose to partner with you?",
                "question_type": "text",
                "sub_section": subsection_objects[
                    "Justification for proposed partnership"
                ],
                "section": section_objects["General Information"],
            },
            {
                "text": "How can your organization help fulfil the mandate of Baylor-Uganda “to achieve HIV epidemic control to attain and sustain the UNAIDS 95-95-95 goals in For-Mubende regions”.",
                "question_type": "text",
                "sub_section": subsection_objects[
                    "Justification for proposed partnership"
                ],
                "section": section_objects["General Information"],
            },
            {
                "text": "What is the context within which this project is being proposed?",
                "question_type": "text",
                "sub_section": subsection_objects[
                    "Problem and Proposed intervention(s)"
                ],
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "text": "What is the overall problem that your organization believes needs to be addressed?",
                "question_type": "text",
                "sub_section": subsection_objects[
                    "Problem and Proposed intervention(s)"
                ],
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "text": "What is the overall rationale for proposed interventions and results?",
                "question_type": "text",
                "sub_section": subsection_objects[
                    "Problem and Proposed intervention(s)"
                ],
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "text": "Proposed Methodology and tools to carry out proposed intervention(s)",
                "question_type": "text",
                "sub_section": subsection_objects[
                    "Justification for proposed intervention(s)"
                ],
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "text": "How does your Organization propose to monitor and/or learn from these interventions?",
                "question_type": "text",
                "sub_section": subsection_objects[
                    "Justification for proposed intervention(s)"
                ],
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "text": "Please indicate the anticipated budget total needed to carry out the work listed above (UGX)",
                "question_type": "number",
                "sub_section": subsection_objects["Budget and Duration"],
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "text": "Please indicate the anticipated project duration needed (maximum 1 year) to carry out the work listed above(months)",
                "question_type": "number",
                "sub_section": subsection_objects["Budget and Duration"],
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "text": "Please describe your organization’s capacity to manage the budget indicated, based on your structure and past history.",
                "question_type": "text",
                "sub_section": subsection_objects["Budget and Duration"],
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "text": "What is the anticipated geographic coverage of your proposed work under this project? (you may choose both)",
                "question_type": "checkbox",
                "choices": ["District", "Sub-counties"],
                "sub_section": subsection_objects["Geographic Coverage"],
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "text": "If you chose both District and Sub-counties, please explain the link between the two in your planned intervention(s).",
                "question_type": "text",
                "sub_section": subsection_objects["Geographic Coverage"],
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "text": "If at District level, please list the sub-counties, your experience in those districts and your presence there currently.",
                "question_type": "table",
                "choices": ["District", "Number of sub-counties within the district within which you propose working", "What experience do you have in this district", "Do you currently have a physical presence in this district?  If not, how do you anticipate covering work here?"],
                "sub_section": subsection_objects["Geographic Coverage"],
                "number_of_rows": 4,
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "text": "What is the relevance of the proposed geographic coverage to the problems/issues identified above?",
                "question_type": "text",
                "sub_section": subsection_objects["Geographic Coverage"],
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "text": "Who are the main stakeholders for this project?",
                "question_type": "text",
                "sub_section": subsection_objects[
                    "Project Stakeholders and Beneficiaries"
                ],
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "text": "Describe how project stakeholders and beneficiaries have been or will be involved in determining the specific work to be done under this project",
                "question_type": "text",
                "sub_section": subsection_objects[
                    "Project Stakeholders and Beneficiaries"
                ],
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "text": "Please describe the potential conflicts related to your intervention and how you will mitigate them.",
                "question_type": "text",
                "sub_section": subsection_objects["Conflict sensitivity"],
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "text": "Please describe the potential risks and assumptions for the work that you are proposing above (Please add rows if needed) Risks and Mitigation strategies",
                "question_type": "text",
                "sub_section": subsection_objects[
                    "What are the risks and assumptions for the proposed work?"
                ],
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "text": "Please describe the potential risks and assumptions for the work that you are proposing above (Please add rows if needed) Assumptions",
                "question_type": "text",
                "sub_section": subsection_objects[
                    "What are the risks and assumptions for the proposed work?"
                ],
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "text": "Please specify which organizations and/or government organs you anticipate working closely with during implementation.",
                "question_type": "table",
                "choices": ["Name of organization or institution", "Contact"],
                "sub_section": subsection_objects["Anticipated partnerships"],
                "number_of_rows": 3,
                "section": section_objects["Proposed Areas of Work and Experience"],
            },
            {
                "text": "Is your organization willing to adhere to and sign a non-discrimination clause if selected by BAYLOR UGANDA (i.e. a clause in the contract where your organization agrees not to discriminate against different groups within the community in your programming).",
                "question_type": "radio",
                "choices": ["Yes", "No"],
                "sub_section": subsection_objects["Non-Discrimination"],
                "section": section_objects["Signature Page"],
            },
            {
                "text": "If no, please describe circumstances under which you would not be able to comply.",
                "question_type": "text",
                "sub_section": subsection_objects["Non-Discrimination"],
                "section": section_objects["Signature Page"],
            },
            {
                "text": "Is your organization willing to adhere to and sign an anti-corruption clause if selected by BAYLOR UGANDA (i.e. a clause in the contract where your organization agrees to zero tolerance for corruption and to report any suspected corruption to BAYLOR UGANDA).",
                "question_type": "radio",
                "choices": ["Yes", "No"],
                "sub_section": subsection_objects["Anti-Corruption"],
                "section": section_objects["Signature Page"],
            },
            {
                "text": "Please be sure to include the following documents listed in the checklist as attachments to your EOI.",
                "question_type": "checkbox",
                "choices": [
                    "Copies of last 3 institutional audit reports and Management Letters",
                    "Certificate of Registration",
                    "Articles of Association and Memorandum of Association (These must include list/contacts of all Directors of the organization)",
                    "Recommendation from the District of operation",
                    "Board Minutes of the recent 2 concluded Board meetings",
                    "Operation permit issued by the NGO Bureau in accordance with the NGO Act 2016",
                    "Organizational Strategic Plan",
                    "Financial Policy",
                    "Human Resource Policy",
                    "HIV at Work Policy",
                    "Children’s Act etc",
                    "Detailed budget (Using the template/format provided)",
                    "Tax (URA) Clearance Certificate and NSSF Clearance Certificate",
                ],
                "sub_section": subsection_objects[
                    "CheckList of Documents to attach to eOi"
                ],
                "section": section_objects["Signature Page"],
            },
            {
                "text": "I hereby certify that the information presented in the application above is, to the best of my knowledge, truthful. I understand that the presentation of false or misleading information in this application may lead to the organization being disqualified from consideration by Baylor Uganda.",
                "question_type": "table",
                "choices": ["Name", "Signature", "Position", "Date"],
                "sub_section": subsection_objects["Signature"],
                "number_of_rows": 1,
                "section": section_objects["Signature Page"],
            },
        ]

        # Create or get questions
        for q in questions:
            DefaultApplicationQuestion.objects.get_or_create(**q)

        self.stdout.write(
            self.style.SUCCESS("Default application questions and sections added")
        )
