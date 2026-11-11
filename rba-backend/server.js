const express = require('express');
const cors = require('cors');
const nodemailer = require('nodemailer');
const crypto = require('crypto'); // built into Node, no install needed

// Credentials are read from the terminal session (never stored in this file)
const EMAIL_USER = process.env.EMAIL_USER;
const EMAIL_PASS = process.env.EMAIL_PASS;

if (!EMAIL_USER || !EMAIL_PASS) {
  console.error('\nMissing EMAIL_USER or EMAIL_PASS. Set them in this terminal first:\n');
  console.error('  $env:EMAIL_USER="youremail@gmail.com"');
  console.error('  $env:EMAIL_PASS="your16letterapppassword"');
  console.error('  node server.js\n');
  process.exit(1);
}

const app = express();
app.use(cors());
app.use(express.json());
app.set('trust proxy', true);

const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: { user: EMAIL_USER, pass: EMAIL_PASS },
});

// In-memory sessions: email -> { otp, score, ip, expires, blocked }
const sessions = {};

const PENALTY = 25;      // points lost per wrong OTP or IP change
const PASS_SCORE = 50;   // score must be >= 50 to be granted access
const OTP_TTL_MS = 5 * 60 * 1000;

function getIp(req) {
  return (req.ip || '').replace('::ffff:', '');
}

// Test route so http://localhost:5000 shows something
app.get('/', (req, res) => {
  res.send('RBA backend is working');
});

// 1. Send OTP
app.post('/send-otp', async (req, res) => {
  const email = (req.body.email || '').trim().toLowerCase();
  if (!email) {
    return res.json({ success: false, message: 'Email is required.' });
  }

  const existing = sessions[email];
  if (existing && existing.blocked) {
    return res.json({
      success: false,
      message: 'This account is locked due to suspicious activity.',
    });
  }

  const otp = crypto.randomInt(1000, 10000).toString(); // 4-digit code
  sessions[email] = {
    otp,
    score: 100,
    ip: getIp(req),
    expires: Date.now() + OTP_TTL_MS,
    blocked: false,
  };

  try {
    await transporter.sendMail({
      from: EMAIL_USER,
      to: email,
      subject: 'Your RBA verification code',
      text: `Your 4-digit OTP is ${otp}. It expires in 5 minutes.`,
    });
    res.json({
      success: true,
      message: 'OTP sent to your Gmail inbox.',
      trustScore: 100,
    });
  } catch (err) {
    console.error('Email error:', err.message);
    res.json({
      success: false,
      message: 'Could not send email. Check EMAIL_USER and your Gmail App Password.',
    });
  }
});

// 2. Verify OTP and apply risk scoring
app.post('/verify-otp', (req, res) => {
  const email = (req.body.email || '').trim().toLowerCase();
  const otp = (req.body.otp || '').trim();
  const s = sessions[email];

  if (!s) {
    return res.json({ status: 'FAILED', message: 'Request an OTP first.', score: 0 });
  }
  if (s.blocked) {
    return res.json({
      status: 'BLOCKED',
      message: 'Access blocked due to suspicious activity.',
      score: s.score,
    });
  }
  if (Date.now() > s.expires) {
    return res.json({
      status: 'FAILED',
      message: 'OTP expired. Request a new one.',
      score: s.score,
    });
  }

  // Deduct points if the IP changed since the OTP was requested
  const currentIp = getIp(req);
  if (currentIp !== s.ip) {
    s.score -= PENALTY;
    s.ip = currentIp;
  }

  // Deduct points for a wrong OTP
  if (otp !== s.otp) {
    s.score -= PENALTY;
  } else if (s.score >= PASS_SCORE) {
    const finalScore = s.score;
    delete sessions[email];
    return res.json({
      status: 'GRANTED',
      message: 'Identity verified. Welcome!',
      score: finalScore,
    });
  }

  // Wrong OTP (or correct OTP but score too low)
  if (s.score < PASS_SCORE) {
    s.blocked = true;
    return res.json({
      status: 'BLOCKED',
      message: 'Too many suspicious attempts. Access blocked.',
      score: s.score,
    });
  }

  res.json({
    status: 'FAILED',
    message: 'Incorrect OTP.',
    score: s.score,
  });
});

app.listen(5000, () => console.log('Project backend running on http://localhost:5000'));