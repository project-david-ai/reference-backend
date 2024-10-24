from flask import jsonify
from datetime import datetime
from . import bp_legal


@bp_legal.route('/privacy-policy', methods=['GET'])
def privacy_policy():
    try:
        content = f"""
        Privacy Statement

        1. Introduction
           - We, Project David Ltd, are committed to protecting the privacy and personal data of our users.
           - This privacy statement explains how we collect, use, and protect your personal information when you use our services.

        2. Data Collection
           - We collect personal information such as your username, email address, first name, last name, and mobile number when you create an account with us.
           - We also store information related to your conversation sessions, including the session ID, creation date, user ID, thread content, thread ID, summary, and messages.
           - When you use our services, we may collect certain information automatically, such as your IP address, browser type, referring/exit pages, operating system, date/time stamp, and clickstream data.

        3. Data Use
           - We use your personal information to provide and improve our services, authenticate your access to our platform, personalize your experience, and communicate with you.
           - We may use your email address to send you important notifications, updates, and relevant information about our services.
           - We may use cookies and similar tracking technologies to enhance your browsing experience, analyze trends, and collect information about your interactions with our services.

        4. Data Protection
           - We implement appropriate technical and organizational measures to protect your personal data from unauthorized access, alteration, disclosure, or destruction.
           - We encrypt sensitive information, such as passwords, using industry-standard practices like bcrypt hashing.
           - Access to your personal data is limited to authorized personnel who need it to perform their duties.
           - We use JWT (JSON Web Tokens) for authentication and store them as cookies with an expiration period of 7 days.

        5. Data Retention
           - We retain your personal information for as long as necessary to fulfill the purposes for which it was collected, comply with legal obligations, resolve disputes, and enforce our agreements.
           - If you close your account, we may retain certain information in an anonymized form for analytical purposes and to prevent fraud.
           - We store confirmation PINs and their expiration dates to verify user email addresses and mobile numbers.

        6. Your Rights
           - As a user residing in the UK/EU area, you have certain rights under the General Data Protection Regulation (GDPR).
           - You have the right to access, rectify, erase, restrict processing, object to processing, and data portability of your personal information.
           - You have the right to withdraw your consent for processing your personal data at any time.
           - To exercise these rights or for any privacy-related inquiries, please contact us using the information provided below.

        7. Third-Party Disclosure
           - We do not sell, trade, or otherwise transfer your personal information to third parties without your consent, except as required by law or to trusted third parties who assist us in operating our services.
           - These third parties are bound by confidentiality obligations and are only permitted to use your personal data for the specified purposes.

        8. International Data Transfers
           - As a company based in the UK, we comply with the GDPR and ensure that any international data transfers are carried out in accordance with applicable data protection laws.
           - If we transfer your personal data outside the UK/EU, we will ensure that appropriate safeguards are in place to protect your rights and freedoms.

        9. Children's Privacy
           - Our services are not intended for use by children under the age of 16.
           - We do not knowingly collect personal information from children under 16. If we become aware that a child under 16 has provided us with personal information, we will take steps to delete such information.

        10. Changes to this Privacy Statement
            - We reserve the right to update or modify this privacy statement at any time.
            - We will notify you of any significant changes by posting the updated version on our website or through other communication channels.
            - The "Last Updated" date at the bottom of this privacy statement indicates when it was last revised.

        11. Contact Us
            - If you have any questions, concerns, or requests regarding this privacy statement or the handling of your personal data, please contact us at [insert contact information].
            - You have the right to lodge a complaint with the UK Information Commissioner's Office (ICO) or your local data protection authority if you believe we have not handled your personal data in accordance with applicable laws.

        This privacy statement is effective as of [insert date].

        Last Updated: {datetime.utcnow().strftime("%Y-%m-%d")}
        """

        return jsonify({'content': content})

    except Exception as e:
        print(f"Error in privacy_policy route: {str(e)}")
        return jsonify({'error': 'Failed to fetch privacy policy content'}), 500


@bp_legal.route('/terms-of-service', methods=['GET'])
def terms_of_service():
    try:
        content = f"""
        Terms of Service

        1. Introduction
           - Welcome to Project David Ltd, an AI research and integration company based in the UK.
           - These Terms of Service ("Terms") govern your use of our AI apps, entities, agents, and associated software applications and websites ("Services").
           - By using our Services, you agree to be bound by these Terms. If you do not agree with any part of these Terms, you must not use our Services.

        2. Eligibility
           - You must be at least 13 years old to use our Services. If you are under 18, you must have your parent or legal guardian's permission to use the Services.
           - If you are using the Services on behalf of an organization, you represent that you have the authority to bind that organization to these Terms.

        3. Use of Services
           - We grant you a limited, non-exclusive, non-transferable, and revocable license to use our Services in accordance with these Terms.
           - You may not use our Services for any illegal, harmful, or abusive purposes, or in a way that violates the rights of others or interferes with the operation of our Services.
           - You are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account.

        4. Intellectual Property
           - Project David Ltd and its licensors own all rights, title, and interest in and to the Services, including all intellectual property rights.
           - You retain ownership of any content you provide as input to our Services ("Input"). By providing Input, you grant us a worldwide, non-exclusive, royalty-free license to use, reproduce, modify, adapt, publish, translate, distribute, and display the Input solely for the purpose of providing and improving our Services.
           - Any output generated by our Services ("Output") is owned by you, subject to any third-party rights or limitations. We do not guarantee the accuracy, completeness, or reliability of the Output.

        5. Privacy
           - We collect and process your personal data in accordance with our Privacy Statement, which is incorporated into these Terms by reference.
           - By using our Services, you consent to the collection, use, and disclosure of your personal data as described in our Privacy Statement.

        6. Termination
           - We may suspend or terminate your access to the Services at any time, without prior notice, for any reason, including if we reasonably believe you have violated these Terms.
           - You may terminate your account and stop using the Services at any time. Termination of your account does not relieve you of any obligations arising prior to termination.

        7. Disclaimer of Warranties
           - Our Services are provided "as is" and "as available" without warranties of any kind, whether express, implied, or statutory, including but not limited to warranties of merchantability, fitness for a particular purpose, and non-infringement.
           - We do not warrant that the Services will be uninterrupted, error-free, or secure, or that any defects will be corrected.

        8. Limitation of Liability
           - To the maximum extent permitted by law, Project David Ltd and its affiliates, officers, employees, agents, and licensors shall not be liable for any indirect, incidental, special, consequential, or punitive damages, or any loss of profits or revenues, whether incurred directly or indirectly, or any loss of data, use, goodwill, or other intangible losses, resulting from your use of the Services or any content accessed through the Services.

        9. Indemnification
           - You agree to indemnify, defend, and hold harmless Project David Ltd and its affiliates, officers, employees, agents, and licensors from and against any claims, liabilities, damages, losses, costs, and expenses, including reasonable attorneys' fees, arising out of or in connection with your use of the Services or violation of these Terms.

        10. Governing Law and Dispute Resolution
            - These Terms shall be governed by and construed in accordance with the laws of England and Wales, without regard to its conflict of law provisions.
            - Any dispute arising out of or in connection with these Terms shall be subject to the exclusive jurisdiction of the courts of England and Wales.

        11. Modification of Terms
            - We reserve the right to modify these Terms at any time. Any changes will be effective immediately upon posting the revised Terms on our website.
            - Your continued use of the Services after the posting of the revised Terms constitutes your acceptance of the modified Terms.

        12. Miscellaneous
            - If any provision of these Terms is found to be invalid, illegal, or unenforceable, the remaining provisions shall continue in full force and effect.
            - Our failure to enforce any right or provision of these Terms shall not be considered a waiver of such right or provision.
            - These Terms constitute the entire agreement between you and Project David Ltd regarding the use of the Services and supersede any prior agreements.

        This Terms of Service is effective as of [insert date].

        Last Updated: {datetime.utcnow().strftime("%Y-%m-%d")}
        """

        return jsonify({'content': content})

    except Exception as e:
        print(f"Error in terms_of_service route: {str(e)}")
        return jsonify({'error': 'Failed to fetch terms of service content'}), 500