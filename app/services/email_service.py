"""
Servicio de envío de emails usando Resend
"""
import resend
from typing import Optional, Dict, Any
from app.core.config import settings
from datetime import datetime


# Configurar API key de Resend
resend.api_key = settings.RESEND_API_KEY


class EmailService:
    """Servicio centralizado para envío de emails"""
    
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
    def send_welcome_email(user_email: str, user_name: str) -> Dict[str, Any]:
        """
        Email de bienvenida al registrarse
        """
        subject = "¡Bienvenido a HighTech RMA System! 🎉"
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #2563eb;">¡Bienvenido a HighTech RMA System!</h1>
                    
                    <p>Hola <strong>{user_name}</strong>,</p>
                    
                    <p>Gracias por registrarte en nuestro sistema de gestión de RMAs. 
                    Tu cuenta ha sido creada exitosamente.</p>
                    
                    <div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">¿Qué puedes hacer ahora?</h3>
                        <ul>
                            <li>Crear solicitudes de RMA para tus productos</li>
                            <li>Hacer seguimiento del estado de tus solicitudes</li>
                            <li>Recibir notificaciones de cada cambio</li>
                        </ul>
                    </div>
                    
                    <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
                    
                    <p style="margin-top: 30px;">
                        Saludos,<br>
                        <strong>Equipo HighTech RMA</strong>
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                    <p style="font-size: 12px; color: #6b7280;">
                        Este es un email automático, por favor no respondas a este mensaje.
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
        temp_password: str
    ) -> Dict[str, Any]:
        """
        Email de bienvenida para usuarios creados por SUPERADMIN
        Incluye contraseña temporal que debe cambiar en el primer login
        """
        role_display = {
            "USER": "Usuario",
            "ADMIN": "Administrador",
            "SUPERADMIN": "Super Administrador"
        }.get(user_role, user_role)
        
        subject = f"🎉 Bienvenido a HighTech RMA System - Cuenta {role_display}"
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background-color: #2563eb; color: white; padding: 20px; border-radius: 5px; text-align: center;">
                        <h1 style="margin: 0;">¡Bienvenido a HighTech RMA System! 🎉</h1>
                    </div>
                    
                    <p style="margin-top: 20px;">Hola <strong>{user_name}</strong>,</p>
                    
                    <p>Tu cuenta ha sido creada exitosamente en nuestro sistema de gestión de RMAs.</p>
                    
                    <div style="background-color: #dbeafe; border-left: 4px solid #2563eb; padding: 20px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #1e40af;">📋 Información de tu Cuenta</h3>
                        <p><strong>Email:</strong> {user_email}</p>
                        <p><strong>Rol:</strong> {role_display}</p>
                        <p style="margin: 15px 0 5px 0;"><strong>Contraseña Temporal:</strong></p>
                        <div style="background-color: white; padding: 12px; border-radius: 5px; font-family: monospace; font-size: 16px; font-weight: bold; color: #dc2626; border: 2px dashed #dc2626;">
                            {temp_password}
                        </div>
                    </div>
                    
                    <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0;">
                        <p style="margin: 0;"><strong>⚠️ Importante:</strong> Esta es una contraseña temporal. 
                        Por seguridad, te recomendamos cambiarla después de tu primer inicio de sesión.</p>
                    </div>
                    
                    <div style="background-color: #f3f4f6; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">🚀 Primeros Pasos</h3>
                        <ol style="margin: 10px 0; padding-left: 20px;">
                            <li>Inicia sesión con tu email y contraseña temporal</li>
                            <li>Actualiza tu perfil con tu información personal</li>
                            <li>Cambia tu contraseña por una más segura</li>
                            <li>Comienza a usar el sistema</li>
                        </ol>
                    </div>
                    
                    <div style="background-color: #e0f2fe; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">🎯 ¿Qué puedes hacer según tu rol?</h3>
                        {
                            '<ul><li>Crear y gestionar solicitudes de RMA</li><li>Ver el estado de tus RMAs</li><li>Recibir notificaciones automáticas</li></ul>' 
                            if user_role == "USER" 
                            else '<ul><li>Gestionar RMAs de tu país</li><li>Ver reportes y estadísticas</li><li>Gestionar usuarios de tu región</li></ul>' 
                            if user_role == "ADMIN"
                            else '<ul><li>Gestión completa del sistema</li><li>Crear y gestionar usuarios de cualquier rol</li><li>Acceso a todos los RMAs y reportes</li></ul>'
                        }
                    </div>
                    
                    <p>Si tienes alguna pregunta o necesitas ayuda, no dudes en contactarnos.</p>
                    
                    <p style="margin-top: 30px;">
                        Saludos,<br>
                        <strong>Equipo HighTech RMA</strong>
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                    <p style="font-size: 12px; color: #6b7280;">
                        Este es un email automático, por favor no respondas a este mensaje.<br>
                        Por tu seguridad, no compartas esta contraseña con nadie.
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
        reset_url: str
    ) -> Dict[str, Any]:
        """
        Email para recuperación de contraseña con token de un solo uso
        El token expira en 1 hora
        """
        subject = "🔐 Recuperación de Contraseña - HighTech RMA System"
        
        full_reset_url = f"{reset_url}?token={reset_token}"
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background-color: #dc2626; color: white; padding: 20px; border-radius: 5px; text-align: center;">
                        <h1 style="margin: 0;">🔐 Recuperación de Contraseña</h1>
                    </div>
                    
                    <p style="margin-top: 20px;">Hola <strong>{user_name}</strong>,</p>
                    
                    <p>Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en HighTech RMA System.</p>
                    
                    <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0;">
                        <p style="margin: 0;"><strong>⚠️ Si no solicitaste este cambio:</strong> 
                        Ignora este mensaje y tu contraseña permanecerá sin cambios. 
                        Tu cuenta está segura.</p>
                    </div>
                    
                    <p>Para restablecer tu contraseña, haz clic en el siguiente botón:</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{full_reset_url}" 
                           style="background-color: #2563eb; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                            Restablecer Contraseña
                        </a>
                    </div>
                    
                    <p style="font-size: 14px; color: #6b7280;">
                        Si el botón no funciona, copia y pega este enlace en tu navegador:
                    </p>
                    <div style="background-color: #f3f4f6; padding: 12px; border-radius: 5px; word-break: break-all; font-size: 12px; font-family: monospace;">
                        {full_reset_url}
                    </div>
                    
                    <div style="background-color: #fee2e2; border-left: 4px solid #dc2626; padding: 15px; margin: 20px 0;">
                        <p style="margin: 0;"><strong>🕐 Este enlace expira en 1 hora</strong></p>
                        <p style="margin: 5px 0 0 0; font-size: 14px;">
                            Por seguridad, el enlace solo puede usarse una vez y tiene una duración limitada.
                        </p>
                    </div>
                    
                    <div style="background-color: #e0f2fe; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">💡 Consejos de Seguridad</h3>
                        <ul style="margin: 5px 0; padding-left: 20px; font-size: 14px;">
                            <li>Usa una contraseña única para cada servicio</li>
                            <li>Combina letras mayúsculas, minúsculas, números y símbolos</li>
                            <li>No compartas tu contraseña con nadie</li>
                            <li>Cambia tu contraseña periódicamente</li>
                        </ul>
                    </div>
                    
                    <p>Si necesitas ayuda o tienes alguna pregunta sobre tu cuenta, no dudes en contactarnos.</p>
                    
                    <p style="margin-top: 30px;">
                        Saludos,<br>
                        <strong>Equipo HighTech RMA</strong>
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                    <p style="font-size: 12px; color: #6b7280;">
                        Este es un email automático, por favor no respondas a este mensaje.<br>
                        Si no solicitaste este cambio, tu cuenta sigue siendo segura.
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
        rma_id: int
    ) -> Dict[str, Any]:
        """
        Email cuando se crea un RMA
        """
        subject = f"RMA Creado - {company_name}"
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #2563eb;">RMA Creado Exitosamente ✅</h1>
                    
                    <p>Hola <strong>{user_name}</strong>,</p>
                    
                    <p>Tu solicitud de RMA ha sido creada correctamente y está en proceso de revisión.</p>
                    
                    <div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">Detalles de la Solicitud</h3>
                        <p><strong>ID:</strong> #{rma_id}</p>
                        <p><strong>Empresa:</strong> {company_name}</p>
                        <p><strong>Productos:</strong> {items_count} item(s)</p>
                        <p><strong>Estado:</strong> <span style="color: #f59e0b;">Pendiente de Revisión</span></p>
                    </div>
                    
                    <p><strong>Próximos pasos:</strong></p>
                    <ol>
                        <li>Nuestro equipo revisará tu solicitud</li>
                        <li>Recibirás un email cuando cambie el estado</li>
                        <li>Si es aprobada, te asignaremos un número de RMA oficial</li>
                    </ol>
                    
                    <p>Recibirás notificaciones por email en cada actualización.</p>
                    
                    <p style="margin-top: 30px;">
                        Saludos,<br>
                        <strong>Equipo HighTech RMA</strong>
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
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Email cuando el RMA es APROBADO
        """
        subject = f"✅ RMA Aprobado - {rma_number}"
        
        comment_section = ""
        if comment:
            comment_section = f"""
            <div style="background-color: #dbeafe; padding: 10px; border-radius: 5px; margin: 15px 0;">
                <strong>Comentario del administrador:</strong><br>
                {comment}
            </div>
            """
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #10b981;">¡Tu RMA ha sido Aprobado! ✅</h1>
                    
                    <p>Hola <strong>{user_name}</strong>,</p>
                    
                    <p>Tenemos buenas noticias. Tu solicitud de RMA ha sido aprobada.</p>
                    
                    <div style="background-color: #d1fae5; padding: 20px; border-radius: 5px; margin: 20px 0; text-align: center;">
                        <h2 style="margin: 0; color: #059669;">Número de RMA Asignado</h2>
                        <p style="font-size: 24px; font-weight: bold; margin: 10px 0; color: #047857;">
                            {rma_number}
                        </p>
                        <p style="margin: 0; font-size: 14px; color: #065f46;">
                            Empresa: {company_name}
                        </p>
                    </div>
                    
                    {comment_section}
                    
                    <p><strong>Por favor guarda este número de RMA</strong> para futuras referencias y comunicaciones.</p>
                    
                    <p><strong>Próximos pasos:</strong></p>
                    <ul>
                        <li>Prepara los productos según las instrucciones</li>
                        <li>Espera indicaciones de envío</li>
                        <li>Mantén este número a mano para consultas</li>
                    </ul>
                    
                    <p style="margin-top: 30px;">
                        Saludos,<br>
                        <strong>Equipo HighTech RMA</strong>
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
        reason: str
    ) -> Dict[str, Any]:
        """
        Email cuando el RMA es RECHAZADO
        """
        subject = f"❌ RMA Rechazado - {company_name}"
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #ef4444;">RMA Rechazado</h1>
                    
                    <p>Hola <strong>{user_name}</strong>,</p>
                    
                    <p>Lamentamos informarte que tu solicitud de RMA <strong>#{rma_id}</strong> 
                    para <strong>{company_name}</strong> ha sido rechazada.</p>
                    
                    <div style="background-color: #fee2e2; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #dc2626;">Motivo del Rechazo</h3>
                        <p style="margin: 0;">{reason}</p>
                    </div>
                    
                    <p><strong>¿Qué puedes hacer?</strong></p>
                    <ul>
                        <li>Revisa el motivo del rechazo detalladamente</li>
                        <li>Corrige la información necesaria</li>
                        <li>Crea una nueva solicitud con los datos correctos</li>
                        <li>Contacta a soporte si necesitas ayuda</li>
                    </ul>
                    
                    <p>Estamos aquí para ayudarte. Si tienes preguntas, no dudes en contactarnos.</p>
                    
                    <p style="margin-top: 30px;">
                        Saludos,<br>
                        <strong>Equipo HighTech RMA</strong>
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
        file_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Email cuando se sube cotización o factura con el PDF adjunto
        """
        doc_name = "Cotización" if attachment_type.upper() == "QUOTE" else "Factura"
        subject = f"📎 {doc_name} Disponible - {rma_number or 'RMA'}"
        
        comment_section = ""
        if comment:
            comment_section = f"""
            <div style="background-color: #dbeafe; padding: 10px; border-radius: 5px; margin: 15px 0;">
                <strong>Mensaje del administrador:</strong><br>
                {comment}
            </div>
            """
        
        # Mensaje de adjunto
        attachment_message = ""
        if file_content and file_name:
            attachment_message = """
            <div style="background-color: #d1fae5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 0;">📎 <strong>El documento está adjunto en este email</strong></p>
                <p style="margin: 5px 0 0 0; font-size: 14px; color: #065f46;">
                    También puedes descargarlo desde tu cuenta en cualquier momento.
                </p>
            </div>
            """
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #2563eb;">Nueva {doc_name} Disponible 📎</h1>
                    
                    <p>Hola <strong>{user_name}</strong>,</p>
                    
                    <p>Hemos cargado una <strong>{doc_name.lower()}</strong> para tu RMA.</p>
                    
                    <div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>RMA:</strong> {rma_number or 'Pendiente de número'}</p>
                        <p><strong>Empresa:</strong> {company_name}</p>
                        <p><strong>Documento:</strong> {doc_name}</p>
                    </div>
                    
                    {comment_section}
                    {attachment_message}
                    
                    <p>Por favor revisa el documento y contáctanos si tienes alguna duda.</p>
                    
                    <p><strong>También puedes acceder al documento:</strong></p>
                    <ol>
                        <li>Iniciando sesión en tu cuenta</li>
                        <li>Accediendo al detalle de tu RMA</li>
                        <li>Descargando desde la sección de adjuntos</li>
                    </ol>
                    
                    <p style="margin-top: 30px;">
                        Saludos,<br>
                        <strong>Equipo HighTech RMA</strong>
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
        tracking_id: str
    ) -> Dict[str, Any]:
        """
        Email cuando el RMA está en envío (IN_SHIPPING)
        """
        subject = f"📦 RMA en Envío - {rma_number}"
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #2563eb;">Tu RMA está en Camino 📦</h1>
                    
                    <p>Hola <strong>{user_name}</strong>,</p>
                    
                    <p>Tu RMA ha sido procesado y está en camino.</p>
                    
                    <div style="background-color: #dbeafe; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">Información de Envío</h3>
                        <p><strong>RMA:</strong> {rma_number}</p>
                        <p><strong>Empresa:</strong> {company_name}</p>
                        <p><strong>Transportadora:</strong> {shipping_company}</p>
                        <p style="margin: 15px 0;">
                            <strong>Número de Rastreo:</strong><br>
                            <span style="font-size: 18px; font-weight: bold; color: #1e40af;">
                                {tracking_id}
                            </span>
                        </p>
                    </div>
                    
                    <p><strong>¿Cómo rastrear tu envío?</strong></p>
                    <ol>
                        <li>Visita el sitio web de <strong>{shipping_company}</strong></li>
                        <li>Ingresa el número de rastreo: <code>{tracking_id}</code></li>
                        <li>Podrás ver el estado actual y ubicación del paquete</li>
                    </ol>
                    
                    <p>Recibirás una notificación cuando el envío sea completado.</p>
                    
                    <p style="margin-top: 30px;">
                        Saludos,<br>
                        <strong>Equipo HighTech RMA</strong>
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
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Email cuando el RMA se completa
        """
        subject = f"✅ RMA Completado - {rma_number}"
        
        comment_section = ""
        if comment:
            comment_section = f"""
            <div style="background-color: #dbeafe; padding: 10px; border-radius: 5px; margin: 15px 0;">
                <strong>Notas finales:</strong><br>
                {comment}
            </div>
            """
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #10b981;">¡RMA Completado! ✅</h1>
                    
                    <p>Hola <strong>{user_name}</strong>,</p>
                    
                    <p>Tu RMA ha sido completado exitosamente.</p>
                    
                    <div style="background-color: #d1fae5; padding: 20px; border-radius: 5px; margin: 20px 0; text-align: center;">
                        <h2 style="margin: 0; color: #059669;">RMA Finalizado</h2>
                        <p style="font-size: 20px; font-weight: bold; margin: 10px 0; color: #047857;">
                            {rma_number}
                        </p>
                        <p style="margin: 0; font-size: 14px; color: #065f46;">
                            {company_name}
                        </p>
                    </div>
                    
                    {comment_section}
                    
                    <p>Gracias por confiar en HighTech RMA System para la gestión de tus productos.</p>
                    
                    <p><strong>¿Necesitas algo más?</strong></p>
                    <ul>
                        <li>Puedes revisar el historial completo en tu cuenta</li>
                        <li>Descarga los documentos finales si los necesitas</li>
                        <li>Contacta a soporte si tienes preguntas</li>
                    </ul>
                    
                    <p>Esperamos poder servirte nuevamente en el futuro.</p>
                    
                    <p style="margin-top: 30px;">
                        Saludos,<br>
                        <strong>Equipo HighTech RMA</strong>
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
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Email genérico para cualquier cambio de estado
        """
        subject = f"📋 Actualización de RMA - {status_display}"
        
        comment_section = ""
        if comment:
            comment_section = f"""
            <div style="background-color: #dbeafe; padding: 10px; border-radius: 5px; margin: 15px 0;">
                <strong>Comentario del administrador:</strong><br>
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
                    <h1 style="color: {color};">Actualización de Estado de RMA</h1>
                    
                    <p>Hola <strong>{user_name}</strong>,</p>
                    
                    <p>El estado de tu RMA ha sido actualizado.</p>
                    
                    <div style="background-color: #f3f4f6; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">Información del RMA</h3>
                        <p><strong>RMA:</strong> {rma_number or 'Pendiente de aprobación'}</p>
                        <p><strong>Empresa:</strong> {company_name}</p>
                        <p><strong>Nuevo Estado:</strong> <span style="color: {color}; font-weight: bold;">{status_display}</span></p>
                    </div>
                    
                    {comment_section}
                    
                    <p>Puedes revisar los detalles completos de tu RMA iniciando sesión en tu cuenta.</p>
                    
                    <p style="margin-top: 30px;">
                        Saludos,<br>
                        <strong>Equipo HighTech RMA</strong>
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                    <p style="font-size: 12px; color: #6b7280;">
                        Recibirás notificaciones en cada actualización de tu RMA.
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
        days_pending: int
    ) -> Dict[str, Any]:
        """
        Email recordatorio de pago pendiente
        Se envía según el intervalo configurado en PAYMENT_REMINDER_INTERVAL_DAYS
        """
        from app.core.config import settings
        
        reminder_interval = settings.PAYMENT_REMINDER_INTERVAL_DAYS
        subject = f"⏰ Recordatorio: Pago Pendiente - RMA {rma_number}"
        
        # Mensaje más urgente según días transcurridos
        # Calculamos múltiplos del intervalo configurado
        if days_pending >= (reminder_interval * 3):  # 3x el intervalo
            urgency_message = "Este es un recordatorio importante. Han transcurrido varios días y aún no hemos recibido confirmación del pago."
            urgency_color = "#dc2626"
        elif days_pending >= (reminder_interval * 2):  # 2x el intervalo
            urgency_message = "Te recordamos que el pago sigue pendiente para poder continuar con el proceso."
            urgency_color = "#ea580c"
        else:  # 1x el intervalo
            urgency_message = "Tu RMA está en espera de pago para poder continuar con el siguiente paso."
            urgency_color = "#f59e0b"
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background-color: {urgency_color}; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                        <h1 style="margin: 0; font-size: 24px;">⏰ Recordatorio de Pago</h1>
                    </div>
                    
                    <p>Hola <strong>{user_name}</strong>,</p>
                    
                    <p>{urgency_message}</p>
                    
                    <div style="background-color: #fef3c7; border-left: 4px solid {urgency_color}; padding: 20px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: {urgency_color};">Información del RMA</h3>
                        <p><strong>RMA:</strong> {rma_number}</p>
                        <p><strong>Empresa:</strong> {company_name}</p>
                        <p><strong>Estado:</strong> <span style="color: #8b5cf6; font-weight: bold;">PAGO PENDIENTE</span></p>
                        <p><strong>Días transcurridos:</strong> {days_pending} días</p>
                    </div>
                    
                    <div style="background-color: #f3f4f6; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">¿Qué necesitas hacer?</h3>
                        <ol style="margin: 10px 0; padding-left: 20px;">
                            <li>Revisa la cotización o factura adjunta en los correos anteriores</li>
                            <li>Realiza el pago según las instrucciones proporcionadas</li>
                            <li>El equipo actualizará el estado una vez confirmado el pago</li>
                        </ol>
                    </div>
                    
                    <p style="background-color: #e0f2fe; padding: 15px; border-radius: 5px; border-left: 4px solid #0284c7;">
                        <strong>💡 Nota:</strong> Si ya realizaste el pago, por favor ignora este mensaje. 
                        Nuestro equipo actualizará el estado en breve.
                    </p>
                    
                    <p>Si tienes alguna duda sobre el proceso de pago o necesitas más información, 
                    no dudes en contactarnos.</p>
                    
                    <p style="margin-top: 30px;">
                        Saludos,<br>
                        <strong>Equipo HighTech RMA</strong>
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                    <p style="font-size: 12px; color: #6b7280;">
                        Recibirás este recordatorio cada {reminder_interval} días hasta que se confirme el pago.
                    </p>
                </div>
            </body>
        </html>
        """
        
        return EmailService._send_email(user_email, subject, html)


# Instancia global del servicio
email_service = EmailService()
