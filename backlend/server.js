const express = require('express');
const cors = require('cors');

const app = express();

// 1. Enable CORS so your frontend can talk to this backend
app.use(cors()); 
app.use(express.json());

// Temporary in-memory storage
// NOTE: Data will reset every time the server restarts (which happens on free tier sleep)
const membersDatabase = [];
const connectionsDatabase = [];

app.post('/api/protocol/submit', (req, res) => {
    const { metadata, fields } = req.body;

    if (!metadata || !fields) {
        return res.status(400).json({ message: "Invalid data format" });
    }

    // --- PROTOCOL INTELLIGENCE & SCORING ---
    let agencyScore = 100;
    let flags = [];

    // 1. Sunk Cost Analysis
    if (metadata.manifesto_ms < 3000) {
        agencyScore -= 30;
        flags.push("SKIPPED_MANIFESTO");
    }

    // 2. Effort Analysis
    if (metadata.vision_ms < 10000) {
        agencyScore -= 40;
        flags.push("LOW_EFFORT_VISION");
    }

    // 3. Network Mapping
    if (fields.inviter && fields.inviter.trim() !== "") {
        connectionsDatabase.push({
            new_member: fields.discord,
            invited_by: fields.inviter,
            timestamp: metadata.ts_end
        });
    } else {
        flags.push("LONE_WOLF");
    }

    // --- CONSTRUCT FINAL RECORD ---
    const memberRecord = {
        internal_id: metadata.id,
        status: "PENDING_REVIEW",
        agency_score: agencyScore,
        risk_flags: flags,
        identity: {
            name: fields.name,
            academic: fields.academic,
            discord: fields.discord,
            reason: fields.reason
        },
        competence: {
            skills: fields.skills,
            proficiency: fields.proficiency,
            vision: fields.vision
        },
        telemetry: {
            started_at: metadata.ts_start,
            completed_at: metadata.ts_end,
            manifesto_time_sec: (metadata.manifesto_ms / 1000).toFixed(2),
            vision_time_sec: (metadata.vision_ms / 1000).toFixed(2)
        }
    };

    membersDatabase.push(memberRecord);

    console.log(`\n[NEW PROTOCOL SUBMISSION] - Agency Score: ${agencyScore}/100`);
    console.log(`Applicant: ${fields.name} (${fields.discord})`);
    console.log(`Flags: ${flags.length > 0 ? flags.join(', ') : 'NONE'}`);
    
    res.status(200).json({ 
        message: "Protocol Received", 
        status: "PENDING",
        received_id: metadata.id 
    });
});

// Add a simple test route so you can check if the server is alive in the browser
app.get('/', (req, res) => {
    res.send("Protocol Intelligence Server is Online 🟢");
});

// --- CRITICAL FIX HERE ---
// Use the port provided by Render (process.env.PORT), otherwise default to 3000 for local testing
const PORT = process.env.PORT || 3000;

app.listen(PORT, '0.0.0.0', () => {
    console.log(`[SYSTEM] Protocol Intelligence Server running on port ${PORT}`);
});