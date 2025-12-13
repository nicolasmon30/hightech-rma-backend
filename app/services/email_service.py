"""
Servicio de envío de emails usando Resend
"""
import resend
from typing import Optional, Dict, Any
from app.core.config import settings
from datetime import datetime


# Configurar API key de Resend
resend.api_key = settings.RESEND_API_KEY


# Traducciones de emails (ES / EN)
EMAIL_TRANSLATIONS = {
    "es": {
        "welcome": {
            "subject": "¡Bienvenido a HighTech RMA System! 🎉",
            "title": "¡Bienvenido a HighTech RMA System!",
            "greeting": "Hola",
            "intro": "Gracias por registrarte en nuestro sistema de gestión de RMAs. Tu cuenta ha sido creada exitosamente.",
            "what_can_do": "¿Qué puedes hacer ahora?",
            "can_do_1": "Crear solicitudes de RMA para tus productos",
            "can_do_2": "Hacer seguimiento del estado de tus solicitudes",
            "can_do_3": "Recibir notificaciones de cada cambio",
            "questions": "Si tienes alguna pregunta, no dudes en contactarnos.",
            "signature": "Equipo HighTech RMA",
            "auto_email": "Este es un email automático, por favor no respondas a este mensaje."
        },
        "admin_welcome": {
            "subject_prefix": "Bienvenido a HighTech RMA System - Cuenta",
            "title": "¡Bienvenido a HighTech RMA System! 🎉",
            "greeting": "Hola",
            "intro": "Tu cuenta ha sido creada exitosamente en nuestro sistema de gestión de RMAs.",
            "account_info": "Información de tu Cuenta",
            "email_label": "Email:",
            "role_label": "Rol:",
            "temp_password": "Contraseña Temporal:",
            "important": "Importante:",
            "important_msg": "Esta es una contraseña temporal. Por seguridad, te recomendamos cambiarla después de tu primer inicio de sesión.",
            "first_steps": "Primeros Pasos",
            "step_1": "Inicia sesión con tu email y contraseña temporal",
            "step_2": "Actualiza tu perfil con tu información personal",
            "step_3": "Cambia tu contraseña por una más segura",
            "step_4": "Comienza a usar el sistema",
            "what_can_do": "¿Qué puedes hacer según tu rol?",
            "user_features": "Crear y gestionar solicitudes de RMA|Ver el estado de tus RMAs|Recibir notificaciones automáticas",
            "admin_features": "Gestionar RMAs de tu país|Ver reportes y estadísticas|Gestionar usuarios de tu región",
            "superadmin_features": "Gestión completa del sistema|Crear y gestionar usuarios de cualquier rol|Acceso a todos los RMAs y reportes",
            "questions": "Si tienes alguna pregunta o necesitas ayuda, no dudes en contactarnos.",
            "signature": "Equipo HighTech RMA",
            "auto_email": "Este es un email automático, por favor no respondas a este mensaje.",
            "security_note": "Por tu seguridad, no compartas esta contraseña con nadie.",
            "roles": {
                "USER": "Usuario",
                "ADMIN": "Administrador",
                "SUPERADMIN": "Super Administrador"
            }
        },
        "password_reset": {
            "subject": "🔐 Recuperación de Contraseña - HighTech RMA System",
            "title": "🔐 Recuperación de Contraseña",
            "greeting": "Hola",
            "intro": "Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en HighTech RMA System.",
            "if_not_you": "Si no solicitaste este cambio:",
            "if_not_you_msg": "Ignora este mensaje y tu contraseña permanecerá sin cambios. Tu cuenta está segura.",
            "reset_instructions": "Para restablecer tu contraseña, haz clic en el siguiente botón:",
            "reset_button": "Restablecer Contraseña",
            "if_button_fails": "Si el botón no funciona, copia y pega este enlace en tu navegador:",
            "expires": "Este enlace expira en 1 hora",
            "expires_msg": "Por seguridad, el enlace solo puede usarse una vez y tiene una duración limitada.",
            "security_tips": "Consejos de Seguridad",
            "tip_1": "Usa una contraseña única para cada servicio",
            "tip_2": "Combina letras mayúsculas, minúsculas, números y símbolos",
            "tip_3": "No compartas tu contraseña con nadie",
            "tip_4": "Cambia tu contraseña periódicamente",
            "questions": "Si necesitas ayuda o tienes alguna pregunta sobre tu cuenta, no dudes en contactarnos.",
            "signature": "Equipo HighTech RMA",
            "auto_email": "Este es un email automático, por favor no respondas a este mensaje.",
            "account_safe": "Si no solicitaste este cambio, tu cuenta sigue siendo segura."
        },
        "rma_created": {
            "subject_prefix": "RMA Creado -",
            "title": "RMA Creado Exitosamente ✅",
            "greeting": "Hola",
            "intro": "Tu solicitud de RMA ha sido creada correctamente y está en proceso de revisión.",
            "details": "Detalles de la Solicitud",
            "id_label": "ID:",
            "company_label": "Empresa:",
            "products_label": "Productos:",
            "status_label": "Estado:",
            "status_pending": "Pendiente de Revisión",
            "next_steps": "Próximos pasos:",
            "step_1": "Nuestro equipo revisará tu solicitud",
            "step_2": "Recibirás un email cuando cambie el estado",
            "step_3": "Si es aprobada, te asignaremos un número de RMA oficial",
            "notifications": "Recibirás notificaciones por email en cada actualización.",
            "signature": "Equipo HighTech RMA"
        },
        "rma_approved": {
            "subject_prefix": "✅ RMA Aprobado -",
            "title": "¡Tu RMA ha sido Aprobado! ✅",
            "greeting": "Hola",
            "intro": "Tenemos buenas noticias. Tu solicitud de RMA ha sido aprobada.",
            "assigned_number": "Número de RMA Asignado",
            "company_label": "Empresa:",
            "admin_comment": "Comentario del administrador:",
            "save_number": "Por favor guarda este número de RMA para futuras referencias y comunicaciones.",
            "next_steps": "Próximos pasos:",
            "step_1": "Prepara los productos según las instrucciones",
            "step_2": "Espera indicaciones de envío",
            "step_3": "Mantén este número a mano para consultas",
            "copy_instructions_1": "Por favor envía tu equipo a la siguiente dirección utilizando la transportadora de tu preferencia.",
            "copy_instructions_2": "Además, imprime una copia en papel del formulario RMA e inclúyela en la caja con tu equipo. ¡Esto nos ayudará a identificar tu equipo!",
            "signature": "Equipo HighTech RMA"
        },
        "rma_rejected": {
            "subject_prefix": "❌ RMA Rechazado -",
            "title": "RMA Rechazado",
            "greeting": "Hola",
            "intro": "Lamentamos informarte que tu solicitud de RMA",
            "for": "para",
            "rejected": "ha sido rechazada.",
            "reason_title": "Motivo del Rechazo",
            "what_can_do": "¿Qué puedes hacer?",
            "action_1": "Revisa el motivo del rechazo detalladamente",
            "action_2": "Corrige la información necesaria",
            "action_3": "Crea una nueva solicitud con los datos correctos",
            "action_4": "Contacta a soporte si necesitas ayuda",
            "help": "Estamos aquí para ayudarte. Si tienes preguntas, no dudes en contactarnos.",
            "signature": "Equipo HighTech RMA"
        },
        "rma_quote_uploaded": {
            "subject_prefix": "📎 {doc_name} Disponible -",
            "title": "Nueva {doc_name} Disponible 📎",
            "quote": "Cotización",
            "invoice": "Factura",
            "greeting": "Hola",
            "intro": "Hemos cargado una",
            "for_your_rma": "para tu RMA.",
            "rma_label": "RMA:",
            "company_label": "Empresa:",
            "document_label": "Documento:",
            "admin_message": "Mensaje del administrador:",
            "attached": "El documento está adjunto en este email",
            "can_download": "También puedes descargarlo desde tu cuenta en cualquier momento.",
            "review": "Por favor revisa el documento y contáctanos si tienes alguna duda.",
            "access_title": "También puedes acceder al documento:",
            "access_1": "Iniciando sesión en tu cuenta",
            "access_2": "Accediendo al detalle de tu RMA",
            "access_3": "Descargando desde la sección de adjuntos",
            "signature": "Equipo HighTech RMA",
            "pending_number": "Pendiente de número"
        },
        "rma_shipping": {
            "subject_prefix": "📦 RMA en Envío -",
            "title": "Tu RMA está en Camino 📦",
            "greeting": "Hola",
            "intro": "Tu RMA ha sido procesado y está en camino.",
            "shipping_info": "Información de Envío",
            "rma_label": "RMA:",
            "company_label": "Empresa:",
            "carrier_label": "Transportadora:",
            "tracking_label": "Número de Rastreo:",
            "how_track": "¿Cómo rastrear tu envío?",
            "track_1": "Visita el sitio web de",
            "track_2": "Ingresa el número de rastreo:",
            "track_3": "Podrás ver el estado actual y ubicación del paquete",
            "notification": "Recibirás una notificación cuando el envío sea completado.",
            "signature": "Equipo HighTech RMA"
        },
        "rma_completed": {
            "subject_prefix": "✅ RMA Completado -",
            "title": "¡RMA Completado! ✅",
            "greeting": "Hola",
            "intro": "Tu RMA ha sido completado exitosamente.",
            "completed_label": "RMA Finalizado",
            "final_notes": "Notas finales:",
            "thanks": "Gracias por confiar en HighTech RMA System para la gestión de tus productos.",
            "need_more": "¿Necesitas algo más?",
            "action_1": "Puedes revisar el historial completo en tu cuenta",
            "action_2": "Descarga los documentos finales si los necesitas",
            "action_3": "Contacta a soporte si tienes preguntas",
            "hope": "Esperamos poder servirte nuevamente en el futuro.",
            "signature": "Equipo HighTech RMA"
        },
        "rma_status_change": {
            "subject_prefix": "📋 Actualización de RMA -",
            "title": "Actualización de Estado de RMA",
            "greeting": "Hola",
            "intro": "El estado de tu RMA ha sido actualizado.",
            "rma_info": "Información del RMA",
            "rma_label": "RMA:",
            "company_label": "Empresa:",
            "new_status": "Nuevo Estado:",
            "admin_comment": "Comentario del administrador:",
            "details": "Puedes revisar los detalles completos de tu RMA iniciando sesión en tu cuenta.",
            "signature": "Equipo HighTech RMA",
            "footer_note": "Recibirás notificaciones en cada actualización de tu RMA.",
            "pending_approval": "Pendiente de aprobación"
        },
        "payment_reminder": {
            "subject_prefix": "⏰ Recordatorio: Pago Pendiente - RMA",
            "title": "⏰ Recordatorio de Pago",
            "greeting": "Hola",
            "urgency_high": "Este es un recordatorio importante. Han transcurrido varios días y aún no hemos recibido confirmación del pago.",
            "urgency_medium": "Te recordamos que el pago sigue pendiente para poder continuar con el proceso.",
            "urgency_low": "Tu RMA está en espera de pago para poder continuar con el siguiente paso.",
            "rma_info": "Información del RMA",
            "rma_label": "RMA:",
            "company_label": "Empresa:",
            "status_label": "Estado:",
            "status_payment": "PAGO PENDIENTE",
            "days_label": "Días transcurridos:",
            "days": "días",
            "what_to_do": "¿Qué necesitas hacer?",
            "action_1": "Revisa la cotización o factura adjunta en los correos anteriores",
            "action_2": "Realiza el pago según las instrucciones proporcionadas",
            "action_3": "El equipo actualizará el estado una vez confirmado el pago",
            "note": "Nota:",
            "note_msg": "Si ya realizaste el pago, por favor ignora este mensaje. Nuestro equipo actualizará el estado en breve.",
            "questions": "Si tienes alguna duda sobre el proceso de pago o necesitas más información, no dudes en contactarnos.",
            "signature": "Equipo HighTech RMA",
            "footer_note": "Recibirás este recordatorio cada {interval} días hasta que se confirme el pago."
        }
    },
    "en": {
        "welcome": {
            "subject": "Welcome to HighTech RMA System! 🎉",
            "title": "Welcome to HighTech RMA System!",
            "greeting": "Hello",
            "intro": "Thank you for registering in our RMA management system. Your account has been successfully created.",
            "what_can_do": "What can you do now?",
            "can_do_1": "Create RMA requests for your products",
            "can_do_2": "Track the status of your requests",
            "can_do_3": "Receive notifications for each update",
            "questions": "If you have any questions, please don't hesitate to contact us.",
            "signature": "HighTech RMA Team",
            "auto_email": "This is an automated email, please do not reply to this message."
        },
        "admin_welcome": {
            "subject_prefix": "Welcome to HighTech RMA System - Account",
            "title": "Welcome to HighTech RMA System! 🎉",
            "greeting": "Hello",
            "intro": "Your account has been successfully created in our RMA management system.",
            "account_info": "Your Account Information",
            "email_label": "Email:",
            "role_label": "Role:",
            "temp_password": "Temporary Password:",
            "important": "Important:",
            "important_msg": "This is a temporary password. For security reasons, we recommend changing it after your first login.",
            "first_steps": "First Steps",
            "step_1": "Log in with your email and temporary password",
            "step_2": "Update your profile with your personal information",
            "step_3": "Change your password to a more secure one",
            "step_4": "Start using the system",
            "what_can_do": "What can you do according to your role?",
            "user_features": "Create and manage RMA requests|View your RMA status|Receive automatic notifications",
            "admin_features": "Manage RMAs in your country|View reports and statistics|Manage users in your region",
            "superadmin_features": "Full system management|Create and manage users of any role|Access to all RMAs and reports",
            "questions": "If you have any questions or need help, please don't hesitate to contact us.",
            "signature": "HighTech RMA Team",
            "auto_email": "This is an automated email, please do not reply to this message.",
            "security_note": "For your security, do not share this password with anyone.",
            "roles": {
                "USER": "User",
                "ADMIN": "Administrator",
                "SUPERADMIN": "Super Administrator"
            }
        },
        "password_reset": {
            "subject": "🔐 Password Recovery - HighTech RMA System",
            "title": "🔐 Password Recovery",
            "greeting": "Hello",
            "intro": "We have received a request to reset the password for your HighTech RMA System account.",
            "if_not_you": "If you did not request this change:",
            "if_not_you_msg": "Ignore this message and your password will remain unchanged. Your account is secure.",
            "reset_instructions": "To reset your password, click the following button:",
            "reset_button": "Reset Password",
            "if_button_fails": "If the button doesn't work, copy and paste this link into your browser:",
            "expires": "This link expires in 1 hour",
            "expires_msg": "For security reasons, the link can only be used once and has a limited duration.",
            "security_tips": "Security Tips",
            "tip_1": "Use a unique password for each service",
            "tip_2": "Combine uppercase letters, lowercase letters, numbers and symbols",
            "tip_3": "Do not share your password with anyone",
            "tip_4": "Change your password periodically",
            "questions": "If you need help or have any questions about your account, please don't hesitate to contact us.",
            "signature": "HighTech RMA Team",
            "auto_email": "This is an automated email, please do not reply to this message.",
            "account_safe": "If you did not request this change, your account is still secure."
        },
        "rma_created": {
            "subject_prefix": "RMA Created -",
            "title": "RMA Successfully Created ✅",
            "greeting": "Hello",
            "intro": "Your RMA request has been successfully created and is under review.",
            "details": "Request Details",
            "id_label": "ID:",
            "company_label": "Company:",
            "products_label": "Products:",
            "status_label": "Status:",
            "status_pending": "Pending Review",
            "next_steps": "Next steps:",
            "step_1": "Our team will review your request",
            "step_2": "You will receive an email when the status changes",
            "step_3": "If approved, we will assign an official RMA number",
            "notifications": "You will receive email notifications for each update.",
            "signature": "HighTech RMA Team"
        },
        "rma_approved": {
            "subject_prefix": "✅ RMA Approved -",
            "title": "Your RMA has been Approved! ✅",
            "greeting": "Hello",
            "intro": "We have good news. Your RMA request has been approved.",
            "assigned_number": "Assigned RMA Number",
            "company_label": "Company:",
            "admin_comment": "Administrator comment:",
            "save_number": "Please save this RMA number for future references and communications.",
            "next_steps": "Next steps:",
            "step_1": "Prepare the products according to the instructions",
            "step_2": "Wait for shipping instructions",
            "step_3": "Keep this number handy for inquiries",
            "copy_instructions_1": "Please send your equipment to the following address below via your carrier of choice.",
            "copy_instructions_2": "Also, please print out a paper copy of the RMA form, and include in the box with your equipment – This will help us identify your equipment!",
            "signature": "HighTech RMA Team"
        },
        "rma_rejected": {
            "subject_prefix": "❌ RMA Rejected -",
            "title": "RMA Rejected",
            "greeting": "Hello",
            "intro": "We regret to inform you that your RMA request",
            "for": "for",
            "rejected": "has been rejected.",
            "reason_title": "Rejection Reason",
            "what_can_do": "What can you do?",
            "action_1": "Review the rejection reason in detail",
            "action_2": "Correct the necessary information",
            "action_3": "Create a new request with the correct data",
            "action_4": "Contact support if you need help",
            "help": "We are here to help you. If you have questions, please don't hesitate to contact us.",
            "signature": "HighTech RMA Team"
        },
        "rma_quote_uploaded": {
            "subject_prefix": "📎 {doc_name} Available -",
            "title": "New {doc_name} Available 📎",
            "quote": "Quote",
            "invoice": "Invoice",
            "greeting": "Hello",
            "intro": "We have uploaded a",
            "for_your_rma": "for your RMA.",
            "rma_label": "RMA:",
            "company_label": "Company:",
            "document_label": "Document:",
            "admin_message": "Administrator message:",
            "attached": "The document is attached to this email",
            "can_download": "You can also download it from your account at any time.",
            "review": "Please review the document and contact us if you have any questions.",
            "access_title": "You can also access the document by:",
            "access_1": "Logging into your account",
            "access_2": "Accessing your RMA details",
            "access_3": "Downloading from the attachments section",
            "signature": "HighTech RMA Team",
            "pending_number": "Pending number"
        },
        "rma_shipping": {
            "subject_prefix": "📦 RMA In Transit -",
            "title": "Your RMA is On Its Way 📦",
            "greeting": "Hello",
            "intro": "Your RMA has been processed and is on its way.",
            "shipping_info": "Shipping Information",
            "rma_label": "RMA:",
            "company_label": "Company:",
            "carrier_label": "Carrier:",
            "tracking_label": "Tracking Number:",
            "how_track": "How to track your shipment?",
            "track_1": "Visit the website of",
            "track_2": "Enter the tracking number:",
            "track_3": "You can view the current status and location of the package",
            "notification": "You will receive a notification when the shipment is completed.",
            "signature": "HighTech RMA Team"
        },
        "rma_completed": {
            "subject_prefix": "✅ RMA Completed -",
            "title": "RMA Completed! ✅",
            "greeting": "Hello",
            "intro": "Your RMA has been successfully completed.",
            "completed_label": "RMA Finished",
            "final_notes": "Final notes:",
            "thanks": "Thank you for trusting HighTech RMA System for managing your products.",
            "need_more": "Need anything else?",
            "action_1": "You can review the complete history in your account",
            "action_2": "Download the final documents if you need them",
            "action_3": "Contact support if you have questions",
            "hope": "We hope to serve you again in the future.",
            "signature": "HighTech RMA Team"
        },
        "rma_status_change": {
            "subject_prefix": "📋 RMA Update -",
            "title": "RMA Status Update",
            "greeting": "Hello",
            "intro": "The status of your RMA has been updated.",
            "rma_info": "RMA Information",
            "rma_label": "RMA:",
            "company_label": "Company:",
            "new_status": "New Status:",
            "admin_comment": "Administrator comment:",
            "details": "You can review the complete details of your RMA by logging into your account.",
            "signature": "HighTech RMA Team",
            "footer_note": "You will receive notifications for each RMA update.",
            "pending_approval": "Pending approval"
        },
        "payment_reminder": {
            "subject_prefix": "⏰ Reminder: Pending Payment - RMA",
            "title": "⏰ Payment Reminder",
            "greeting": "Hello",
            "urgency_high": "This is an important reminder. Several days have passed and we have not yet received payment confirmation.",
            "urgency_medium": "We remind you that payment is still pending to continue with the process.",
            "urgency_low": "Your RMA is awaiting payment to proceed to the next step.",
            "rma_info": "RMA Information",
            "rma_label": "RMA:",
            "company_label": "Company:",
            "status_label": "Status:",
            "status_payment": "PENDING PAYMENT",
            "days_label": "Days elapsed:",
            "days": "days",
            "what_to_do": "What do you need to do?",
            "action_1": "Review the quote or invoice attached in previous emails",
            "action_2": "Make the payment according to the instructions provided",
            "action_3": "The team will update the status once payment is confirmed",
            "note": "Note:",
            "note_msg": "If you have already made the payment, please ignore this message. Our team will update the status shortly.",
            "questions": "If you have any questions about the payment process or need more information, please don't hesitate to contact us.",
            "signature": "HighTech RMA Team",
            "footer_note": "You will receive this reminder every {interval} days until payment is confirmed."
        }
    }
}


class EmailService:
    """Servicio centralizado para envío de emails"""
    
    @staticmethod
    def _get_translation(language: str, section: str) -> Dict[str, str]:
        """
        Obtener traducciones para un idioma y sección específica
        
        Args:
            language: Código de idioma ('es' o 'en')
            section: Sección de traducción (ej: 'welcome', 'rma_created')
        
        Returns:
            Diccionario con traducciones
        """
        # Validar idioma
        lang = language.lower() if language.lower() in ["es", "en"] else "en"
        return EMAIL_TRANSLATIONS.get(lang, EMAIL_TRANSLATIONS["en"]).get(section, {})
    
    @staticmethod
    def _send_email(
        to: str,
        subject: str,
        html: str,
        from_email: Optional[str] = None,
        attachments: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Enviar email usando Resend
        
        Args:
            to: Email del destinatario
            subject: Asunto del email
            html: Contenido HTML del email
            from_email: Email del remitente (opcional)
            attachments: Lista de adjuntos en formato Resend (opcional)
        
        Returns:
            Response de Resend
        """
        if not settings.EMAIL_ENABLED:
            print(f"📧 [SIMULADO] Email a {to}: {subject}")
            if attachments:
                print(f"   📎 Con {len(attachments)} adjunto(s)")
            return {"id": "simulated", "message": "Email disabled in settings"}
        
        try:
            params = {
                "from": from_email or settings.EMAIL_FROM,
                "to": [to],
                "subject": subject,
                "html": html,
            }
            
            # Agregar adjuntos si existen
            if attachments:
                params["attachments"] = attachments
            
            response = resend.Emails.send(params)
            print(f"✅ Email enviado a {to}: {subject}")
            if attachments:
                print(f"   📎 Con {len(attachments)} adjunto(s)")
            return response
        
        except Exception as e:
            print(f"❌ Error enviando email a {to}: {str(e)}")
            raise
    
    
    @staticmethod
    def send_welcome_email(user_email: str, user_name: str, language: str = "en") -> Dict[str, Any]:
        """
        Email de bienvenida al registrarse
        
        Args:
            user_email: Email del usuario
            user_name: Nombre del usuario
            language: Idioma del email ('es' o 'en')
        """
        t = EmailService._get_translation(language, "welcome")
        subject = t["subject"]
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #2563eb;">{t["title"]}</h1>
                    
                    <p>{t["greeting"]} <strong>{user_name}</strong>,</p>
                    
                    <p>{t["intro"]}</p>
                    
                    <div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">{t["what_can_do"]}</h3>
                        <ul>
                            <li>{t["can_do_1"]}</li>
                            <li>{t["can_do_2"]}</li>
                            <li>{t["can_do_3"]}</li>
                        </ul>
                    </div>
                    
                    <p>{t["questions"]}</p>
                    
                    <p style="margin-top: 30px;">
                        <strong>{t["signature"]}</strong>
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                    <p style="font-size: 12px; color: #6b7280;">
                        {t["auto_email"]}
                    </p>
                </div>
            </body>
        </html>
        """
        
        return EmailService._send_email(user_email, subject, html)
    
    
    @staticmethod
    def send_admin_welcome_email(
        user_email: str, 
        user_name: str, 
        user_role: str,
        temp_password: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Email de bienvenida para usuarios creados por SUPERADMIN
        Incluye contraseña temporal que debe cambiar en el primer login
        
        Args:
            user_email: Email del usuario
            user_name: Nombre del usuario
            user_role: Rol del usuario (USER, ADMIN, SUPERADMIN)
            temp_password: Contraseña temporal
            language: Idioma del email ('es' o 'en')
        """
        t = EmailService._get_translation(language, "admin_welcome")
        role_display = t["roles"].get(user_role, user_role)
        
        subject = f"🎉 {t['subject_prefix']} {role_display}"
        
        # Obtener las características según el rol
        if user_role == "USER":
            features_list = t["user_features"].split("|")
        elif user_role == "ADMIN":
            features_list = t["admin_features"].split("|")
        else:  # SUPERADMIN
            features_list = t["superadmin_features"].split("|")
        
        features_html = "<ul>" + "".join([f"<li>{f}</li>" for f in features_list]) + "</ul>"
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background-color: #2563eb; color: white; padding: 20px; border-radius: 5px; text-align: center;">
                        <h1 style="margin: 0;">{t["title"]}</h1>
                    </div>
                    
                    <p style="margin-top: 20px;">{t["greeting"]} <strong>{user_name}</strong>,</p>
                    
                    <p>{t["intro"]}</p>
                    
                    <div style="background-color: #dbeafe; border-left: 4px solid #2563eb; padding: 20px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #1e40af;">📋 {t["account_info"]}</h3>
                        <p><strong>{t["email_label"]}</strong> {user_email}</p>
                        <p><strong>{t["role_label"]}</strong> {role_display}</p>
                        <p style="margin: 15px 0 5px 0;"><strong>{t["temp_password"]}</strong></p>
                        <div style="background-color: white; padding: 12px; border-radius: 5px; font-family: monospace; font-size: 16px; font-weight: bold; color: #dc2626; border: 2px dashed #dc2626;">
                            {temp_password}
                        </div>
                    </div>
                    
                    <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0;">
                        <p style="margin: 0;"><strong>⚠️ {t["important"]}</strong> {t["important_msg"]}</p>
                    </div>
                    
                    <div style="background-color: #f3f4f6; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">🚀 {t["first_steps"]}</h3>
                        <ol style="margin: 10px 0; padding-left: 20px;">
                            <li>{t["step_1"]}</li>
                            <li>{t["step_2"]}</li>
                            <li>{t["step_3"]}</li>
                            <li>{t["step_4"]}</li>
                        </ol>
                    </div>
                    
                    <div style="background-color: #e0f2fe; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">🎯 {t["what_can_do"]}</h3>
                        {features_html}
                    </div>
                    
                    <p>{t["questions"]}</p>
                    
                    <p style="margin-top: 30px;">
                        <strong>{t["signature"]}</strong>
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                    <p style="font-size: 12px; color: #6b7280;">
                        {t["auto_email"]}<br>
                        {t["security_note"]}
                    </p>
                </div>
            </body>
        </html>
        """
        
        return EmailService._send_email(user_email, subject, html)
    
    
    @staticmethod
    def send_password_reset_email(
        user_email: str,
        user_name: str,
        reset_token: str,
        reset_url: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Email para recuperación de contraseña con token de un solo uso
        El token expira en 1 hora
        
        Args:
            user_email: Email del usuario
            user_name: Nombre del usuario
            reset_token: Token de recuperación
            reset_url: URL base para reset
            language: Idioma del email ('es' o 'en')
        """
        t = EmailService._get_translation(language, "password_reset")
        subject = t["subject"]
        
        full_reset_url = f"{reset_url}?token={reset_token}"
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background-color: #dc2626; color: white; padding: 20px; border-radius: 5px; text-align: center;">
                        <h1 style="margin: 0;">{t["title"]}</h1>
                    </div>
                    
                    <p style="margin-top: 20px;">{t["greeting"]} <strong>{user_name}</strong>,</p>
                    
                    <p>{t["intro"]}</p>
                    
                    <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0;">
                        <p style="margin: 0;"><strong>⚠️ {t["if_not_you"]}</strong> 
                        {t["if_not_you_msg"]}</p>
                    </div>
                    
                    <p>{t["reset_instructions"]}</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{full_reset_url}" 
                           style="background-color: #2563eb; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                            {t["reset_button"]}
                        </a>
                    </div>
                    
                    <p style="font-size: 14px; color: #6b7280;">
                        {t["if_button_fails"]}
                    </p>
                    <div style="background-color: #f3f4f6; padding: 12px; border-radius: 5px; word-break: break-all; font-size: 12px; font-family: monospace;">
                        {full_reset_url}
                    </div>
                    
                    <div style="background-color: #fee2e2; border-left: 4px solid #dc2626; padding: 15px; margin: 20px 0;">
                        <p style="margin: 0;"><strong>🕐 {t["expires"]}</strong></p>
                        <p style="margin: 5px 0 0 0; font-size: 14px;">
                            {t["expires_msg"]}
                        </p>
                    </div>
                    
                    <div style="background-color: #e0f2fe; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">💡 {t["security_tips"]}</h3>
                        <ul style="margin: 5px 0; padding-left: 20px; font-size: 14px;">
                            <li>{t["tip_1"]}</li>
                            <li>{t["tip_2"]}</li>
                            <li>{t["tip_3"]}</li>
                            <li>{t["tip_4"]}</li>
                        </ul>
                    </div>
                    
                    <p>{t["questions"]}</p>
                    
                    <p style="margin-top: 30px;">
                        <strong>{t["signature"]}</strong>
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                    <p style="font-size: 12px; color: #6b7280;">
                        {t["auto_email"]}<br>
                        {t["account_safe"]}
                    </p>
                </div>
            </body>
        </html>
        """
        
        return EmailService._send_email(user_email, subject, html)
    
    
    @staticmethod
    def send_rma_created_email(
        user_email: str,
        user_name: str,
        company_name: str,
        items_count: int,
        rma_id: int,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Email cuando se crea un RMA
        
        Args:
            user_email: Email del usuario
            user_name: Nombre del usuario
            company_name: Nombre de la empresa
            items_count: Cantidad de items
            rma_id: ID del RMA
            language: Idioma del email ('es' o 'en')
        """
        t = EmailService._get_translation(language, "rma_created")
        subject = f"{t['subject_prefix']} {company_name}"
        
        rma_url = f"{settings.FRONTEND_URL}/rma"
        view_button_text = "Ver mis RMAs" if language == "es" else "View My RMAs"
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #2563eb;">{t["title"]}</h1>
                    
                    <p>{t["greeting"]} <strong>{user_name}</strong>,</p>
                    
                    <p>{t["intro"]}</p>
                    
                    <div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">{t["details"]}</h3>
                        <p><strong>{t["id_label"]}</strong> #{rma_id}</p>
                        <p><strong>{t["company_label"]}</strong> {company_name}</p>
                        <p><strong>{t["products_label"]}</strong> {items_count} item(s)</p>
                        <p><strong>{t["status_label"]}</strong> <span style="color: #f59e0b;">{t["status_pending"]}</span></p>
                    </div>
                    
                    <p><strong>{t["next_steps"]}</strong></p>
                    <ol>
                        <li>{t["step_1"]}</li>
                        <li>{t["step_2"]}</li>
                        <li>{t["step_3"]}</li>
                    </ol>
                    
                    <p>{t["notifications"]}</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{rma_url}" 
                           style="background-color: #2563eb; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                            {view_button_text}
                        </a>
                    </div>
                    
                    <p style="margin-top: 30px;">
                        <strong>{t["signature"]}</strong>
                    </p>
                </div>
            </body>
        </html>
        """
        
        return EmailService._send_email(user_email, subject, html)
    
    
    @staticmethod
    def send_rma_approved_email(
        user_email: str,
        user_name: str,
        rma_number: str,
        company_name: str,
        comment: Optional[str] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Email cuando el RMA es APROBADO
        
        Args:
            user_email: Email del usuario
            user_name: Nombre del usuario
            rma_number: Número de RMA
            company_name: Nombre de la empresa
            comment: Comentario opcional del administrador
            language: Idioma del email ('es' o 'en')
        """
        t = EmailService._get_translation(language, "rma_approved")
        subject = f"{t['subject_prefix']} {rma_number}"
        
        rma_url = f"{settings.FRONTEND_URL}/rma"
        view_button_text = "Ver mis RMAs" if language == "es" else "View My RMAs"
        
        comment_section = ""
        if comment:
            comment_section = f"""
            <div style="background-color: #dbeafe; padding: 10px; border-radius: 5px; margin: 15px 0;">
                <strong>{t["admin_comment"]}</strong><br>
                {comment}
            </div>
            """
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #10b981;">{t["title"]}</h1>
                    
                    <p>{t["greeting"]} <strong>{user_name}</strong>,</p>
                    
                    <p>{t["intro"]}</p>
                    
                    <div style="background-color: #d1fae5; padding: 20px; border-radius: 5px; margin: 20px 0; text-align: center;">
                        <h2 style="margin: 0; color: #059669;">{t["assigned_number"]}</h2>
                        <p style="font-size: 24px; font-weight: bold; margin: 10px 0; color: #047857;">
                            {rma_number}
                        </p>
                        <p style="margin: 0; font-size: 14px; color: #065f46;">
                            {t["company_label"]} {company_name}
                        </p>
                    </div>
                    
                    {comment_section}
                    
                    <p><strong>{t["save_number"]}</strong></p>
                    
                    <p><strong>{t["next_steps"]}</strong></p>
                    <ul>
                        <li>{t["step_1"]}</li>
                        <li>{t["step_2"]}</li>
                        <li>{t["step_3"]}</li>
                    </ul>
                    <p>
                        {t["copy_instructions_1"]}
                    </p>
                    <p>
                        {t["copy_instructions_2"]}
                    </p>
                    <p>
                        High Tech Supplies, Inc.<br>
                        12601 NW 115 Ave, Building A<br>
                        Unit 114<br>
                        Medley FL 33178<br>
                        USA
                    </p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{rma_url}" 
                           style="background-color: #10b981; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                            {view_button_text}
                        </a>
                    </div>
                    
                    <p style="margin-top: 30px;">
                        <strong>{t["signature"]}</strong>
                    </p>
                </div>
            </body>
        </html>
        """
        
        return EmailService._send_email(user_email, subject, html)
    
    
    @staticmethod
    def send_rma_rejected_email(
        user_email: str,
        user_name: str,
        company_name: str,
        rma_id: int,
        reason: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Email cuando el RMA es RECHAZADO
        
        Args:
            user_email: Email del usuario
            user_name: Nombre del usuario
            company_name: Nombre de la empresa
            rma_id: ID del RMA
            reason: Razón del rechazo
            language: Idioma del email ('es' o 'en')
        """
        t = EmailService._get_translation(language, "rma_rejected")
        subject = f"{t['subject_prefix']} {company_name}"
        
        rma_url = f"{settings.FRONTEND_URL}/rma"
        view_button_text = "Ver mis RMAs" if language == "es" else "View My RMAs"
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #ef4444;">{t["title"]}</h1>
                    
                    <p>{t["greeting"]} <strong>{user_name}</strong>,</p>
                    
                    <p>{t["intro"]} <strong>#{rma_id}</strong> 
                    {t["for"]} <strong>{company_name}</strong> {t["rejected"]}</p>
                    
                    <div style="background-color: #fee2e2; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #dc2626;">{t["reason_title"]}</h3>
                        <p style="margin: 0;">{reason}</p>
                    </div>
                    
                    <p><strong>{t["what_can_do"]}</strong></p>
                    <ul>
                        <li>{t["action_1"]}</li>
                        <li>{t["action_2"]}</li>
                        <li>{t["action_3"]}</li>
                        <li>{t["action_4"]}</li>
                    </ul>
                    
                    <p>{t["help"]}</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{rma_url}" 
                           style="background-color: #2563eb; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                            {view_button_text}
                        </a>
                    </div>
                    
                    <p style="margin-top: 30px;">
                        <strong>{t["signature"]}</strong>
                    </p>
                </div>
            </body>
        </html>
        """
        
        return EmailService._send_email(user_email, subject, html)
    
    
    @staticmethod
    def send_rma_quote_uploaded_email(
        user_email: str,
        user_name: str,
        rma_number: Optional[str],
        company_name: str,
        attachment_type: str,
        comment: Optional[str] = None,
        file_content: Optional[bytes] = None,
        file_name: Optional[str] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Email cuando se sube cotización o factura con el PDF adjunto
        
        Args:
            user_email: Email del usuario
            user_name: Nombre del usuario
            rma_number: Número de RMA (opcional)
            company_name: Nombre de la empresa
            attachment_type: Tipo de adjunto (QUOTE o INVOICE)
            comment: Comentario opcional del administrador
            file_content: Contenido del archivo (opcional)
            file_name: Nombre del archivo (opcional)
            language: Idioma del email ('es' o 'en')
        """
        t = EmailService._get_translation(language, "rma_quote_uploaded")
        doc_name = t["quote"] if attachment_type.upper() == "QUOTE" else t["invoice"]
        subject = t["subject_prefix"].format(doc_name=doc_name) + f" {rma_number or 'RMA'}"
        
        comment_section = ""
        if comment:
            comment_section = f"""
            <div style="background-color: #dbeafe; padding: 10px; border-radius: 5px; margin: 15px 0;">
                <strong>{t["admin_message"]}</strong><br>
                {comment}
            </div>
            """
        
        # Mensaje de adjunto
        attachment_message = ""
        if file_content and file_name:
            attachment_message = f"""
            <div style="background-color: #d1fae5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 0;">📎 <strong>{t["attached"]}</strong></p>
                <p style="margin: 5px 0 0 0; font-size: 14px; color: #065f46;">
                    {t["can_download"]}
                </p>
            </div>
            """
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #2563eb;">{t["title"].format(doc_name=doc_name)}</h1>
                    
                    <p>{t["greeting"]} <strong>{user_name}</strong>,</p>
                    
                    <p>{t["intro"]} <strong>{doc_name.lower()}</strong> {t["for_your_rma"]}</p>
                    
                    <div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>{t["rma_label"]}</strong> {rma_number or t["pending_number"]}</p>
                        <p><strong>{t["company_label"]}</strong> {company_name}</p>
                        <p><strong>{t["document_label"]}</strong> {doc_name}</p>
                    </div>
                    
                    {comment_section}
                    {attachment_message}
                    
                    <p>{t["review"]}</p>
                    
                    <p><strong>{t["access_title"]}</strong></p>
                    <ol>
                        <li>{t["access_1"]}</li>
                        <li>{t["access_2"]}</li>
                        <li>{t["access_3"]}</li>
                    </ol>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{settings.FRONTEND_URL}/rma" 
                           style="background-color: #2563eb; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                            {"Ver mis RMAs" if language == "es" else "View My RMAs"}
                        </a>
                    </div>
                    
                    <p style="margin-top: 30px;">
                        <strong>{t["signature"]}</strong>
                    </p>
                </div>
            </body>
        </html>
        """
        
        # Preparar adjuntos para Resend
        attachments = None
        if file_content and file_name:
            import base64
            attachments = [{
                "filename": file_name,
                "content": base64.b64encode(file_content).decode('utf-8')
            }]
        
        return EmailService._send_email(user_email, subject, html, attachments=attachments)
    
    
    @staticmethod
    def send_rma_shipping_email(
        user_email: str,
        user_name: str,
        rma_number: str,
        company_name: str,
        shipping_company: str,
        tracking_id: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Email cuando el RMA está en envío (IN_SHIPPING)
        
        Args:
            user_email: Email del usuario
            user_name: Nombre del usuario
            rma_number: Número de RMA
            company_name: Nombre de la empresa
            shipping_company: Compañía de envío
            tracking_id: Número de rastreo
            language: Idioma del email ('es' o 'en')
        """
        t = EmailService._get_translation(language, "rma_shipping")
        subject = f"{t['subject_prefix']} {rma_number}"
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #2563eb;">{t["title"]}</h1>
                    
                    <p>{t["greeting"]} <strong>{user_name}</strong>,</p>
                    
                    <p>{t["intro"]}</p>
                    
                    <div style="background-color: #dbeafe; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">{t["shipping_info"]}</h3>
                        <p><strong>{t["rma_label"]}</strong> {rma_number}</p>
                        <p><strong>{t["company_label"]}</strong> {company_name}</p>
                        <p><strong>{t["carrier_label"]}</strong> {shipping_company}</p>
                        <p style="margin: 15px 0;">
                            <strong>{t["tracking_label"]}</strong><br>
                            <span style="font-size: 18px; font-weight: bold; color: #1e40af;">
                                {tracking_id}
                            </span>
                        </p>
                    </div>
                    
                    <p><strong>{t["how_track"]}</strong></p>
                    <ol>
                        <li>{t["track_1"]} <strong>{shipping_company}</strong></li>
                        <li>{t["track_2"]} <code>{tracking_id}</code></li>
                        <li>{t["track_3"]}</li>
                    </ol>
                    
                    <p>{t["notification"]}</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{settings.FRONTEND_URL}/rma" 
                           style="background-color: #06b6d4; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                            {"Ver mis RMAs" if language == "es" else "View My RMAs"}
                        </a>
                    </div>
                    
                    <p style="margin-top: 30px;">
                        <strong>{t["signature"]}</strong>
                    </p>
                </div>
            </body>
        </html>
        """
        
        return EmailService._send_email(user_email, subject, html)
    
    
    @staticmethod
    def send_rma_completed_email(
        user_email: str,
        user_name: str,
        rma_number: str,
        company_name: str,
        comment: Optional[str] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Email cuando el RMA se completa
        
        Args:
            user_email: Email del usuario
            user_name: Nombre del usuario
            rma_number: Número de RMA
            company_name: Nombre de la empresa
            comment: Comentario opcional del administrador
            language: Idioma del email ('es' o 'en')
        """
        t = EmailService._get_translation(language, "rma_completed")
        subject = f"{t['subject_prefix']} {rma_number}"
        
        comment_section = ""
        if comment:
            comment_section = f"""
            <div style="background-color: #dbeafe; padding: 10px; border-radius: 5px; margin: 15px 0;">
                <strong>{t["final_notes"]}</strong><br>
                {comment}
            </div>
            """
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #10b981;">{t["title"]}</h1>
                    
                    <p>{t["greeting"]} <strong>{user_name}</strong>,</p>
                    
                    <p>{t["intro"]}</p>
                    
                    <div style="background-color: #d1fae5; padding: 20px; border-radius: 5px; margin: 20px 0; text-align: center;">
                        <h2 style="margin: 0; color: #059669;">{t["completed_label"]}</h2>
                        <p style="font-size: 20px; font-weight: bold; margin: 10px 0; color: #047857;">
                            {rma_number}
                        </p>
                        <p style="margin: 0; font-size: 14px; color: #065f46;">
                            {company_name}
                        </p>
                    </div>
                    
                    {comment_section}
                    
                    <p>{t["thanks"]}</p>
                    
                    <p><strong>{t["need_more"]}</strong></p>
                    <ul>
                        <li>{t["action_1"]}</li>
                        <li>{t["action_2"]}</li>
                        <li>{t["action_3"]}</li>
                    </ul>
                    
                    <p>{t["hope"]}</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{settings.FRONTEND_URL}/rma" 
                           style="background-color: #10b981; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                            {"Ver mis RMAs" if language == "es" else "View My RMAs"}
                        </a>
                    </div>
                    
                    <p style="margin-top: 30px;">
                        <strong>{t["signature"]}</strong>
                    </p>
                </div>
            </body>
        </html>
        """
        
        return EmailService._send_email(user_email, subject, html)
    
    
    @staticmethod
    def send_rma_status_change_email(
        user_email: str,
        user_name: str,
        rma_number: Optional[str],
        company_name: str,
        new_status: str,
        status_display: str,
        comment: Optional[str] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Email genérico para cualquier cambio de estado
        
        Args:
            user_email: Email del usuario
            user_name: Nombre del usuario
            rma_number: Número de RMA (opcional)
            company_name: Nombre de la empresa
            new_status: Nuevo estado del RMA
            status_display: Estado a mostrar (puede estar traducido)
            comment: Comentario opcional del administrador
            language: Idioma del email ('es' o 'en')
        """
        t = EmailService._get_translation(language, "rma_status_change")
        subject = f"{t['subject_prefix']} {status_display}"
        
        comment_section = ""
        if comment:
            comment_section = f"""
            <div style="background-color: #dbeafe; padding: 10px; border-radius: 5px; margin: 15px 0;">
                <strong>{t["admin_comment"]}</strong><br>
                {comment}
            </div>
            """
        
        # Colores según el estado
        status_colors = {
            "rma_submitted": "#f59e0b",
            "awaiting_goods": "#f59e0b",
            "evaluating": "#3b82f6",
            "processing": "#3b82f6",
            "payment": "#8b5cf6",
            "in_repair": "#3b82f6",
            "approved": "#10b981",
            "rejected": "#ef4444",
            "in_shipping": "#06b6d4",
            "completed": "#10b981"
        }
        
        color = status_colors.get(new_status, "#6b7280")
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: {color};">{t["title"]}</h1>
                    
                    <p>{t["greeting"]} <strong>{user_name}</strong>,</p>
                    
                    <p>{t["intro"]}</p>
                    
                    <div style="background-color: #f3f4f6; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">{t["rma_info"]}</h3>
                        <p><strong>{t["rma_label"]}</strong> {rma_number or t["pending_approval"]}</p>
                        <p><strong>{t["company_label"]}</strong> {company_name}</p>
                        <p><strong>{t["new_status"]}</strong> <span style="color: {color}; font-weight: bold;">{status_display}</span></p>
                    </div>
                    
                    {comment_section}
                    
                    <p>{t["details"]}</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{settings.FRONTEND_URL}/rma" 
                           style="background-color: {color}; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                            {"Ver mis RMAs" if language == "es" else "View My RMAs"}
                        </a>
                    </div>
                    
                    <p style="margin-top: 30px;">
                        <strong>{t["signature"]}</strong>
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                    <p style="font-size: 12px; color: #6b7280;">
                        {t["footer_note"]}
                    </p>
                </div>
            </body>
        </html>
        """
        
        return EmailService._send_email(user_email, subject, html)


    @staticmethod
    def send_payment_reminder_email(
        user_email: str,
        user_name: str,
        rma_number: str,
        company_name: str,
        days_pending: int,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Email recordatorio de pago pendiente
        Se envía según el intervalo configurado en PAYMENT_REMINDER_INTERVAL_DAYS
        
        Args:
            user_email: Email del usuario
            user_name: Nombre del usuario
            rma_number: Número de RMA
            company_name: Nombre de la empresa
            days_pending: Días pendientes
            language: Idioma del email ('es' o 'en')
        """
        from app.core.config import settings
        
        t = EmailService._get_translation(language, "payment_reminder")
        reminder_interval = settings.PAYMENT_REMINDER_INTERVAL_DAYS
        subject = f"{t['subject_prefix']} {rma_number}"
        
        # Mensaje más urgente según días transcurridos
        # Calculamos múltiplos del intervalo configurado
        if days_pending >= (reminder_interval * 3):  # 3x el intervalo
            urgency_message = t["urgency_high"]
            urgency_color = "#dc2626"
        elif days_pending >= (reminder_interval * 2):  # 2x el intervalo
            urgency_message = t["urgency_medium"]
            urgency_color = "#ea580c"
        else:  # 1x el intervalo
            urgency_message = t["urgency_low"]
            urgency_color = "#f59e0b"
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background-color: {urgency_color}; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                        <h1 style="margin: 0; font-size: 24px;">{t["title"]}</h1>
                    </div>
                    
                    <p>{t["greeting"]} <strong>{user_name}</strong>,</p>
                    
                    <p>{urgency_message}</p>
                    
                    <div style="background-color: #fef3c7; border-left: 4px solid {urgency_color}; padding: 20px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: {urgency_color};">{t["rma_info"]}</h3>
                        <p><strong>{t["rma_label"]}</strong> {rma_number}</p>
                        <p><strong>{t["company_label"]}</strong> {company_name}</p>
                        <p><strong>{t["status_label"]}</strong> <span style="color: #8b5cf6; font-weight: bold;">{t["status_payment"]}</span></p>
                        <p><strong>{t["days_label"]}</strong> {days_pending} {t["days"]}</p>
                    </div>
                    
                    <div style="background-color: #f3f4f6; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">{t["what_to_do"]}</h3>
                        <ol style="margin: 10px 0; padding-left: 20px;">
                            <li>{t["action_1"]}</li>
                            <li>{t["action_2"]}</li>
                            <li>{t["action_3"]}</li>
                        </ol>
                    </div>
                    
                    <p style="background-color: #e0f2fe; padding: 15px; border-radius: 5px; border-left: 4px solid #0284c7;">
                        <strong>💡 {t["note"]}</strong> {t["note_msg"]}
                    </p>
                    
                    <p>{t["questions"]}</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{settings.FRONTEND_URL}/rma" 
                           style="background-color: {urgency_color}; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                            {"Ver mis RMAs" if language == "es" else "View My RMAs"}
                        </a>
                    </div>
                    
                    <p style="margin-top: 30px;">
                        <strong>{t["signature"]}</strong>
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                    <p style="font-size: 12px; color: #6b7280;">
                        {t["footer_note"].format(interval=reminder_interval)}
                    </p>
                </div>
            </body>
        </html>
        """
        
        return EmailService._send_email(user_email, subject, html)


# Instancia global del servicio
email_service = EmailService()
