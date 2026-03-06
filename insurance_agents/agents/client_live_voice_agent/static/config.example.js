// Zava Insurance - Voice Agent Configuration
// Copy this file to config.js and replace with your actual values
// config.js should NOT be committed to version control

window.AZURE_CONFIG = {
    endpoint: "https://your-voice-resource.cognitiveservices.azure.com/",
    apiKey: "YOUR_AZURE_VOICE_API_KEY_HERE",
    model: "gpt-4o-realtime-preview",
    voice: "en-US-JennyMultilingualNeural"
};

window.COSMOS_CONFIG = {
    endpoint: "https://your-cosmos-account.documents.azure.com:443/",
    key: "YOUR_COSMOS_DB_PRIMARY_KEY_HERE",
    database: "insurance",
    container: "claim_details"
};

window.VOICE_CONFIG = window.AZURE_CONFIG;

console.log('✅ Zava Insurance Config loaded');
