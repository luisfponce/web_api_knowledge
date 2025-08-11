from fastapi import HTTPException
from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from core.config import smtp_conf

async def send_email(to: EmailStr, username: str):
    try:
        message = MessageSchema(
            subject="Welcome to Bank App!",
            recipients=[to],
            body=f"Hello {username}, welcome to Bank App!",
            subtype=MessageType.html,
        )
        # Send the email using FastMail
        fm = FastMail(smtp_conf)
        await fm.send_message(message, template_name="welcome.html")
        
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
