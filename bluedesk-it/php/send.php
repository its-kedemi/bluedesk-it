<?php
declare(strict_types=1);

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

require __DIR__ . '/phpmailer/Exception.php';
require __DIR__ . '/phpmailer/PHPMailer.php';
require __DIR__ . '/phpmailer/SMTP.php';

$cfg = require __DIR__ . '/config.php';

function back(array $cfg, string $status): void {
    header('Location: ' . $cfg['redirect'] . '?sent=' . $status . '#contact');
    exit;
}
function clean(string $v, int $max): string {
    $v = trim(preg_replace('/[\r\n]+/', ' ', $v) ?? '');
    return mb_substr($v, 0, $max);
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { back($cfg, '0'); }

// Spam trap: real visitors never fill this hidden field.
if (!empty($_POST['website'])) { back($cfg, '1'); }

// Simple rate limit: one request per 30 seconds per visitor IP.
$ip   = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
$lock = sys_get_temp_dir() . '/bluedesk_' . md5($ip);
if (is_file($lock) && time() - (int)filemtime($lock) < 30) { back($cfg, '0'); }
@touch($lock);

$name     = clean((string)($_POST['name'] ?? ''), 100);
$business = clean((string)($_POST['business'] ?? ''), 120);
$email    = clean((string)($_POST['email'] ?? ''), 150);
$phone    = clean((string)($_POST['phone'] ?? ''), 30);
$size     = clean((string)($_POST['size'] ?? ''), 40);
$plan     = clean((string)($_POST['plan'] ?? ''), 40);
$message  = trim(mb_substr((string)($_POST['message'] ?? ''), 0, 2000));

if ($name === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) { back($cfg, '0'); }

$body = "New website enquiry\n\n"
      . "Name: $name\nBusiness: $business\nEmail: $email\nPhone: $phone\n"
      . "Team size: $size\nPlan: $plan\n\nMessage:\n$message\n";

try {
    $mail = new PHPMailer(true);
    $mail->isSMTP();
    $mail->Host       = $cfg['smtp_host'];
    $mail->SMTPAuth   = true;
    $mail->Username   = $cfg['smtp_user'];
    $mail->Password   = $cfg['smtp_pass'];
    $mail->SMTPSecure = $cfg['smtp_secure'] === 'ssl' ? PHPMailer::ENCRYPTION_SMTPS : PHPMailer::ENCRYPTION_STARTTLS;
    $mail->Port       = (int)$cfg['smtp_port'];
    $mail->CharSet    = 'UTF-8';

    $mail->setFrom($cfg['from_email'], $cfg['from_name']);
    $mail->addAddress($cfg['to_email']);
    $mail->addReplyTo($email, $name);
    $mail->Subject = 'Free IT check request from ' . $name . ($business !== '' ? " ($business)" : '');
    $mail->Body    = $body;
    $mail->send();

    if (!empty($cfg['auto_reply'])) {
        $reply = new PHPMailer(true);
        $reply->isSMTP();
        $reply->Host       = $cfg['smtp_host'];
        $reply->SMTPAuth   = true;
        $reply->Username   = $cfg['smtp_user'];
        $reply->Password   = $cfg['smtp_pass'];
        $reply->SMTPSecure = $mail->SMTPSecure;
        $reply->Port       = $mail->Port;
        $reply->CharSet    = 'UTF-8';
        $reply->setFrom($cfg['from_email'], 'BlueDesk IT');
        $reply->addAddress($email, $name);
        $reply->Subject = 'We received your request – BlueDesk IT';
        $reply->Body    = "Hi $name,\n\nThank you for contacting BlueDesk IT. We've received your request for a free IT health check and will reply within one working day.\n\nBlueDesk IT\ninfo@bluedesk.co.ke\n";
        $reply->send();
    }
    back($cfg, '1');
} catch (Exception $e) {
    error_log('BlueDesk mail error: ' . $e->getMessage());
    back($cfg, '0');
}
