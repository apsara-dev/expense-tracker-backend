"""
HTML Email Templates for FinTrack Wealth Hub
Compatible with Gmail (Mobile & Web), Apple Mail, Outlook, and all major email clients.
"""

def get_base_email_template(preheader, content_html):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <title>FinTrack Notification</title>
  <style>
    body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
    table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
    img {{ -ms-interpolation-mode: bicubic; border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }}
    table {{ border-collapse: collapse !important; }}
    body {{ height: 100% !important; margin: 0 !important; padding: 0 !important; width: 100% !important; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }}
    @media screen and (max-width: 600px) {{
      .email-container {{ width: 100% !important; }}
      .otp-code {{ font-size: 28px !important; letter-spacing: 6px !important; }}
      .content-padding {{ padding: 24px 20px !important; }}
    }}
  </style>
</head>
<body style="margin: 0; padding: 0; background-color: #f1f5f9;">
  <!-- PREHEADER (invisible preview text) -->
  <div style="display: none; font-size: 1px; color: #fefefe; line-height: 1px; font-family: sans-serif; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden;">
    {preheader}
  </div>

  <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f1f5f9; padding: 40px 10px;">
    <tr>
      <td align="center">
        <!-- MAIN CONTAINER -->
        <table border="0" cellpadding="0" cellspacing="0" width="100%" class="email-container" style="max-width: 560px; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.06); border: 1px solid #e2e8f0;">
          
          <!-- BRAND HEADER -->
          <tr>
            <td align="center" style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); padding: 32px 20px; text-align: center;">
              <table border="0" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center">
                    <div style="display: inline-block; background: rgba(255,255,255,0.2); width: 48px; height: 48px; border-radius: 12px; line-height: 48px; font-size: 26px; text-align: center; margin-bottom: 8px;">
                      💎
                    </div>
                  </td>
                </tr>
                <tr>
                  <td align="center" style="color: #ffffff; font-size: 24px; font-weight: 800; letter-spacing: -0.5px; margin: 0; text-shadow: 0 1px 2px rgba(0,0,0,0.1);">
                    FinTrack
                  </td>
                </tr>
                <tr>
                  <td align="center" style="color: rgba(255,255,255,0.85); font-size: 13px; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; margin-top: 4px;">
                    Wealth & Expense Hub
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- BODY CONTENT -->
          <tr>
            <td class="content-padding" style="padding: 36px 36px 28px 36px; color: #334155;">
              {content_html}
            </td>
          </tr>

          <!-- FOOTER -->
          <tr>
            <td style="background-color: #f8fafc; padding: 24px 36px; border-top: 1px solid #f1f5f9; text-align: center;">
              <p style="margin: 0 0 8px 0; font-size: 12px; color: #94a3b8;">
                🛡️ This is an automated security notification from FinTrack.
              </p>
              <p style="margin: 0; font-size: 11px; color: #cbd5e1;">
                &copy; 2026 FinTrack Wealth Management. All rights reserved.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

def render_otp_email_html(username, otp_code, title="Security Verification", purpose="login to your FinTrack account", validity_minutes=10):
    preheader = f"Your FinTrack verification code is {otp_code}. Valid for {validity_minutes} minutes."
    
    # Split digits for clean presentation if needed
    formatted_otp = " ".join(list(str(otp_code).strip()))

    content = f"""
      <h2 style="margin: 0 0 12px 0; font-size: 20px; font-weight: 700; color: #0f172a;">
        {title} 🔐
      </h2>
      <p style="margin: 0 0 20px 0; font-size: 15px; line-height: 24px; color: #475569;">
        Hello <strong>{username}</strong>,<br>
        We received a request to {purpose}. Use the verification code below to proceed:
      </p>

      <!-- OTP BADGE -->
      <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin: 28px 0;">
        <tr>
          <td align="center" style="background: #f8fafc; border: 2px dashed #6366f1; border-radius: 12px; padding: 20px 16px; text-align: center;">
            <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; color: #6366f1; margin-bottom: 8px;">
              Your 6-Digit OTP Code
            </div>
            <div class="otp-code" style="font-family: 'SF Mono', Consolas, Monaco, 'Courier New', monospace; font-size: 34px; font-weight: 800; letter-spacing: 8px; color: #1e1b4b; margin: 4px 0;">
              {formatted_otp}
            </div>
            <div style="font-size: 12px; color: #64748b; margin-top: 8px;">
              ⏱️ Expires in <strong>{validity_minutes} minutes</strong>
            </div>
          </td>
        </tr>
      </table>

      <!-- SECURITY NOTICE -->
      <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #fffbeb; border: 1px solid #fef3c7; border-radius: 10px; padding: 14px 16px; margin-bottom: 24px;">
        <tr>
          <td style="font-size: 13px; line-height: 20px; color: #92400e;">
            <strong>⚠️ Security Tip:</strong> Never share this code with anyone. FinTrack staff will never ask for your verification code or password.
          </td>
        </tr>
      </table>

      <p style="margin: 0; font-size: 13px; line-height: 20px; color: #64748b;">
        If you did not make this request, you can safely ignore this email or change your password if you suspect unauthorized activity.
      </p>
    """
    return get_base_email_template(preheader, content)


def render_welcome_email_html(username, email):
    preheader = f"Welcome to FinTrack, {username}! Start taking control of your finances today."

    content = f"""
      <h2 style="margin: 0 0 12px 0; font-size: 22px; font-weight: 700; color: #0f172a;">
        Welcome to FinTrack, {username}! 🚀
      </h2>
      <p style="margin: 0 0 18px 0; font-size: 15px; line-height: 24px; color: #475569;">
        We're excited to have you on board! FinTrack gives you total clarity over your money, spending habits, and financial goals.
      </p>

      <!-- FEATURE HIGHLIGHTS -->
      <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f8fafc; border-radius: 12px; padding: 20px; margin: 20px 0; border: 1px solid #e2e8f0;">
        <tr>
          <td style="padding-bottom: 12px; font-size: 14px; color: #334155;">
            📊 <strong>Smart Analytics:</strong> Track income, expense breakdown & monthly cashflow
          </td>
        </tr>
        <tr>
          <td style="padding-bottom: 12px; font-size: 14px; color: #334155;">
            🎯 <strong>Monthly Targets:</strong> Set spending budgets and monitor progress
          </td>
        </tr>
        <tr>
          <td style="padding-bottom: 12px; font-size: 14px; color: #334155;">
            📑 <strong>Instant Reports:</strong> Download Excel (.xlsx) and printable PDF reports
          </td>
        </tr>
        <tr>
          <td style="font-size: 14px; color: #334155;">
            🛡️ <strong>Ironclad Security:</strong> Two-factor OTP authentication protecting your data
          </td>
        </tr>
      </table>

      <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin: 24px 0 12px 0;">
        <tr>
          <td align="center">
            <a href="https://apsarar.pythonanywhere.com/" style="display: inline-block; background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: #ffffff; text-decoration: none; font-size: 15px; font-weight: 700; padding: 14px 32px; border-radius: 10px; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.35);">
              Open FinTrack Dashboard →
            </a>
          </td>
        </tr>
      </table>

      <p style="margin: 20px 0 0 0; font-size: 13px; color: #64748b;">
        Your registered email: <strong>{email}</strong>
      </p>
    """
    return get_base_email_template(preheader, content)
