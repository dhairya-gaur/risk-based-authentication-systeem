# risk-based-authentication-systeem
# 🛡️ Risk-Based Authentication (RBA) System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](#)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#contributing)

An adaptive authentication engine that evaluates **contextual risk signals** in real time — device, location, behavior, and network reputation — and dynamically adjusts authentication requirements (allow, step-up MFA, or block) instead of relying on static passwords alone.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Risk Scoring Flow](#-risk-scoring-flow)
- [Authentication Sequence](#-authentication-sequence)
- [Risk Signal Breakdown](#-risk-signal-breakdown)
- [Decision Matrix](#-decision-matrix)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Configuration](#-configuration)
- [API Reference](#-api-reference)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🔍 Overview

Traditional authentication treats every login attempt the same way. **Risk-Based Authentication (RBA)** instead computes a real-time risk score per session using multiple signals, then chooses a proportionate response:

- ✅ **Low risk** → seamless login, no friction
- ⚠️ **Medium risk** → step-up challenge (OTP, push notification, biometric)
- ⛔ **High risk** → block, alert, or require manual review

This reduces friction for legitimate users while raising the bar for attackers, credential-stuffing bots, and account takeover attempts.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🌍 Geo-velocity checks | Detects impossible travel between logins |
| 📱 Device fingerprinting | Flags new/unrecognized devices |
| 🕵️ Behavioral biometrics | Typing cadence, mouse movement, session patterns |
| 🌐 IP reputation | Cross-checks against threat intel & VPN/Tor lists |
| 🔐 Adaptive MFA | Step-up authentication triggered only when needed |
| 📊 Real-time risk scoring | Weighted scoring engine, sub-100ms decisioning |
| 🧠 ML-based anomaly detection | Learns per-user baseline behavior over time |
| 📈 Audit dashboard | Full visibility into risk decisions and overrides |

---

## 🏗 System Architecture

```mermaid
flowchart TB
    subgraph Client["👤 Client Layer"]
        A[Web / Mobile App]
    end

    subgraph Gateway["🚪 API Gateway"]
        B[Auth Request Handler]
    end

    subgraph RBA["🧠 Risk Engine Core"]
        C[Signal Collector]
        D[Risk Scoring Service]
        E[Policy Decision Engine]
        F[ML Anomaly Model]
    end

    subgraph Data["🗄️ Data Layer"]
        G[(User Behavior Store)]
        H[(Device Fingerprint DB)]
        I[(Threat Intel Feed)]
    end

    subgraph Response["🔁 Response Layer"]
        J[Allow Session]
        K[Step-Up MFA]
        L[Block / Alert SOC]
    end

    A -->|Login Request| B
    B --> C
    C --> D
    C -.reads.-> G
    C -.reads.-> H
    C -.reads.-> I
    D --> F
    F --> D
    D --> E
    E -->|Low Risk| J
    E -->|Medium Risk| K
    E -->|High Risk| L
    K -->|Verified| J
    K -->|Failed| L
```

---

## 📊 Risk Scoring Flow

```mermaid
flowchart LR
    Start([Login Attempt]) --> Collect[Collect Signals]
    Collect --> Device{New Device?}
    Device -- Yes --> DS[+30 pts]
    Device -- No --> DS0[+0 pts]

    Collect --> Loc{Unusual Location?}
    Loc -- Yes --> LS[+25 pts]
    Loc -- No --> LS0[+0 pts]

    Collect --> IP{Bad IP Reputation?}
    IP -- Yes --> IS[+35 pts]
    IP -- No --> IS0[+0 pts]

    Collect --> Behavior{Anomalous Behavior?}
    Behavior -- Yes --> BS[+20 pts]
    Behavior -- No --> BS0[+0 pts]

    DS --> Sum[Aggregate Score]
    DS0 --> Sum
    LS --> Sum
    LS0 --> Sum
    IS --> Sum
    IS0 --> Sum
    BS --> Sum
    BS0 --> Sum

    Sum --> Decision{Total Score}
    Decision -- "0–30" --> Allow[✅ Allow]
    Decision -- "31–70" --> Step[⚠️ Step-Up MFA]
    Decision -- "71+" --> Block[⛔ Block / Review]
```

---

## 🔄 Authentication Sequence

```mermaid
sequenceDiagram
    actor U as User
    participant App as Client App
    participant GW as API Gateway
    participant RE as Risk Engine
    participant MFA as MFA Service
    participant DB as Data Stores

    U->>App: Enter credentials
    App->>GW: POST /auth/login
    GW->>RE: Evaluate risk(context)
    RE->>DB: Fetch device/location/behavior history
    DB-->>RE: Historical profile
    RE->>RE: Compute risk score

    alt Low Risk
        RE-->>GW: ALLOW
        GW-->>App: Session token issued
        App-->>U: ✅ Logged in
    else Medium Risk
        RE-->>GW: STEP_UP required
        GW->>MFA: Trigger OTP/Push
        MFA-->>U: Send challenge
        U->>MFA: Submit response
        MFA-->>GW: Verified
        GW-->>App: Session token issued
        App-->>U: ✅ Logged in (verified)
    else High Risk
        RE-->>GW: BLOCK
        GW-->>App: Access denied
        App-->>U: ⛔ Blocked / contact support
        RE->>DB: Log incident + alert SOC
    end
```

---

## 🧩 Risk Signal Breakdown

```mermaid
pie showData
    title Relative Weight of Risk Signals
    "IP Reputation" : 35
    "Device Fingerprint" : 30
    "Geo-Velocity" : 25
    "Behavioral Anomaly" : 20
    "Time-of-Day Pattern" : 10
```

---

## 🧮 Decision Matrix

```mermaid
quadrantChart
    title Risk Response Matrix
    x-axis Low Confidence --> High Confidence
    y-axis Low Risk --> High Risk
    quadrant-1 Block / Escalate
    quadrant-2 Step-Up MFA
    quadrant-3 Allow Silently
    quadrant-4 Monitor Passively
    New device + bad IP: [0.8, 0.85]
    Known device + new location: [0.6, 0.5]
    Trusted device + normal pattern: [0.9, 0.1]
    Unknown device + normal pattern: [0.3, 0.4]
```

---

## 🛠 Tech Stack

- **Backend:** Node.js / Python (FastAPI)
- **Risk Engine:** Custom scoring service + ML model (scikit-learn / TensorFlow)
- **Cache/Session:** Redis
- **Database:** PostgreSQL (user & audit data), MongoDB (behavioral logs)
- **Messaging:** Kafka (event streaming for real-time signals)
- **MFA Providers:** Twilio / Firebase / WebAuthn
- **Threat Intel:** IPQualityScore / AbuseIPDB integration
- **Infra:** Docker, Kubernetes

---

## 🚀 Getting Started

### Prerequisites
- Node.js ≥ 18 or Python ≥ 3.10
- Docker & Docker Compose
- Redis & PostgreSQL instances

### Installation

```bash
git clone https://github.com/your-org/risk-based-auth.git
cd risk-based-auth
cp .env.example .env
docker-compose up -d
npm install        # or: pip install -r requirements.txt
npm run migrate
npm run dev
```

### Quick Test

```bash
curl -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123","deviceId":"dev-001"}'
```

---

## ⚙️ Configuration

Risk thresholds and weights are configurable in `config/risk-policy.yaml`:

```yaml
thresholds:
  allow_max: 30
  stepup_max: 70
  block_min: 71

weights:
  new_device: 30
  unusual_location: 25
  bad_ip_reputation: 35
  behavioral_anomaly: 20

mfa:
  provider: twilio
  methods: [otp, push]
```

---

## 📡 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/auth/login` | POST | Initiate login, returns risk decision |
| `/auth/mfa/verify` | POST | Submit step-up MFA response |
| `/auth/risk/score` | GET | Retrieve last computed risk score (admin) |
| `/auth/audit-log` | GET | Fetch historical auth decisions |

---

## 🗺 Roadmap

- [ ] Passwordless / WebAuthn-first flow
- [ ] Federated risk sharing across tenants
- [ ] Real-time graph-based fraud ring detection
- [ ] Explainable AI risk score breakdown for end users
- [ ] SOC2 / ISO 27001 audit log export

---

## 🤝 Contributing

Contributions are welcome! Please open an issue to discuss major changes before submitting a PR.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/xyz`)
3. Commit your changes
4. Push and open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.