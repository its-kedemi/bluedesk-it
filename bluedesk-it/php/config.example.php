<?php
// SMTP settings for BlueDesk IT. Fill in the password, then keep this file private.
// Never put these details in index.html: anything in the HTML is visible to every visitor.
return [
    'smtp_host'   => 'mail.bluedesk.co.ke',   // your host's mail server (cPanel hosts usually use mail.yourdomain)
    'smtp_port'   => 587,                      // 587 with STARTTLS (use 465 with 'ssl' if your host requires it)
    'smtp_secure' => 'tls',                    // 'tls' for port 587, 'ssl' for port 465
    'smtp_user'   => 'info@bluedesk.co.ke',
    'smtp_pass'   => 'YOUR_MAILBOX_PASSWORD',              // the mailbox password
    'from_email'  => 'info@bluedesk.co.ke',    // must match the authenticated mailbox
    'from_name'   => 'BlueDesk IT Website',
    'to_email'    => 'info@bluedesk.co.ke',    // where enquiries arrive
    'auto_reply'  => true,                     // send the visitor a confirmation email
    'redirect'    => 'index.html',
];
