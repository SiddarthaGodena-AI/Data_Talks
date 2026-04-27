document.addEventListener("DOMContentLoaded", () => {
    const uploadForm = document.getElementById("uploadForm");
    const transcribeButton = document.getElementById("transcribeButton");
    const analyzeSentimentButton = document.getElementById("analyzeSentimentButton");
    const speakerSentimentButton = document.getElementById("speakerSentimentButton");
    const extractInsightsButton = document.getElementById("extractInsightsButton");
    const generateSummaryButton = document.getElementById("generateSummaryButton");
    const generateMessagesButton = document.getElementById("generateMessagesButton");
    const askButton = document.getElementById("askButton");

    let gcsUri = "";
    let filename = "";
    let transcriptText = "";

    // Upload file
    uploadForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const fileInput = document.getElementById("fileInput").files[0];

        if (!fileInput) {
            alert("Please select a file to upload.");
            return;
        }

        const formData = new FormData();
        formData.append("file", fileInput);

        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const result = await response.json();
        if (result.gcs_uri) {
            gcsUri = result.gcs_uri;
            filename = result.filename;
            document.getElementById("uploadResult").textContent = `File uploaded successfully: ${filename}`;
        } else {
            document.getElementById("uploadResult").textContent = `Error: ${result.error}`;
        }
    });

    // Transcription
    transcribeButton.addEventListener("click", async () => {
        if (!gcsUri || !filename) {
            alert("Please upload a file first.");
            return;
        }

        const response = await fetch("/transcribe", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ gcs_uri: gcsUri, filename: filename })
        });

        const result = await response.json();
        if (result.transcript_text) {
            transcriptText = result.transcript_text;
            document.getElementById("transcriptionResult").textContent = transcriptText;
        } else {
            document.getElementById("transcriptionResult").textContent = `Error: ${result.error}`;
        }
    });

    // Sentiment Analysis
    analyzeSentimentButton.addEventListener("click", async () => {
        if (!transcriptText) {
            alert("Please generate the transcript first.");
            return;
        }

        const response = await fetch("/analyze_sentiment", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ transcript_text: transcriptText })
        });

        const result = await response.json();
        document.getElementById("sentimentResult").textContent = JSON.stringify(result.sentiment, null, 2);
    });

    // Speaker Wise Sentiment Analysis
    speakerSentimentButton.addEventListener("click", async () => {
        if (!transcriptText) {
            alert("Please generate the transcript first.");
            return;
        }
    
        const response = await fetch("/speaker_sentiment", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ transcript_text: transcriptText })
        });
    
        const result = await response.json();
    
        if (result.speaker_sentiment) {
            document.getElementById("speakerSentimentResult").textContent = JSON.stringify(result.speaker_sentiment, null, 2);
        } else {
            document.getElementById("speakerSentimentResult").textContent = `Error: ${result.error}`;
        }
    });

    // Extract Insights
    extractInsightsButton.addEventListener("click", async () => {
        if (!transcriptText) {
            alert("Please generate the transcript first.");
            return;
        }

        const response = await fetch("/extract_insights", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ transcript_text: transcriptText })
        });

        const result = await response.json();
        document.getElementById("insightsResult").textContent = JSON.stringify(result.insights, null, 2);
    });

    // Generate Summary
    generateSummaryButton.addEventListener("click", async () => {
        if (!transcriptText) {
            alert("Please generate the transcript first.");
            return;
        }

        const response = await fetch("/generate_summary", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ transcript_text: transcriptText })
        });

        const result = await response.json();
        document.getElementById("summaryResult").textContent = result.summary;
    });

    // Generate Messages
    generateMessagesButton.addEventListener("click", async () => {
        if (!transcriptText) {
            alert("Please generate the transcript first.");
            return;
        }

        const response = await fetch("/generate_messages", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ transcript_text: transcriptText })
        });

        const result = await response.json();
        document.getElementById("messagesResult").textContent = JSON.stringify(result.messages, null, 2);
    });

    // Ask a Question
    askButton.addEventListener("click", async () => {
        const question = document.getElementById("questionInput").value;

        if (!transcriptText || !question) {
            alert("Please generate the transcript and enter a question.");
            return;
        }

        const response = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ transcript_text: transcriptText, question: question })
        });

        const result = await response.json();
        document.getElementById("questionResult").textContent = result.answer || `Error: ${result.error}`;
    });
});
