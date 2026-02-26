const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors()); // Allows your HTML file to communicate with this server
app.use(express.json());

// Temporary in-memory storage (until you connect a real database)
const membersDatabase = [];
const connectionsDatabase = [];

app.post('/api/protocol/submit', (req, res) => {
    const { metadata, fields } = req.body;

    // --- PROTOCOL INTELLIGENCE & SCORING ---
    let agencyScore = 100;
    let flags = [];

    // 1. Sunk Cost Analysis (Manifesto Reading Time)
    // If they scrolled through 150 words in less than 3 seconds, they didn't read it.
    if (metadata.manifesto_ms < 3000) {
        agencyScore -= 30;
        flags.push("SKIPPED_MANIFESTO");
    }

    // 2. Effort Analysis (Vision Typing Time)
    // If they spent less than 10 seconds on their vision, it's low effort or copy/pasted.
    if (metadata.vision_ms < 10000) {
        agencyScore -= 40;
        flags.push("LOW_EFFORT_VISION");
    }

    // 3. Network Mapping (Referral Edge)
    if (fields.inviter && fields.inviter.trim() !== "") {
        connectionsDatabase.push({
            new_member: fields.discord,
            invited_by: fields.inviter,
            timestamp: metadata.ts_end
        });
    } else {
        flags.push("LONE_WOLF"); // No social proof
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

    // Save to our temporary database
    membersDatabase.push(memberRecord);

    console.log(`\n[NEW PROTOCOL SUBMISSION] - Agency Score: ${agencyScore}/100`);
    console.log(`Applicant: ${fields.name} (${fields.discord})`);
    console.log(`Flags: ${flags.length > 0 ? flags.join(', ') : 'NONE'}`);
    
    // Respond to the frontend
    res.status(200).json({ 
        message: "Protocol Received", 
        status: "PENDING",
        received_id: metadata.id 
    });
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`[SYSTEM] Protocol Intelligence Server running on port ${PORT}`);
});