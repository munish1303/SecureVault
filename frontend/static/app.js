function setStrengthUI(barEl, labelEl, entropyEl, analysis) {
    if (!analysis || !barEl || !labelEl || !entropyEl) {
        return;
    }

    barEl.style.width = `${Math.max(6, analysis.score)}%`;
    labelEl.textContent = `Strength: ${analysis.label.toUpperCase()}`;
    entropyEl.textContent = `Entropy: ${analysis.entropy} bits`;
}

async function copyWithTimeout(text) {
    if (!navigator.clipboard || !text) {
        return false;
    }

    await navigator.clipboard.writeText(text);
    setTimeout(async () => {
        try {
            await navigator.clipboard.writeText("");
        } catch (error) {
            console.warn("Clipboard clear failed.", error);
        }
    }, 15000);

    return true;
}

document.addEventListener("DOMContentLoaded", () => {
    const revealModal = document.getElementById("revealModal");
    const deleteModal = document.getElementById("deleteModal");
    const revealedOutput = document.getElementById("revealedOutput");
    const revealedPassword = document.getElementById("revealedPassword");
    const revealEntryId = document.getElementById("revealEntryId");
    const revealDescription = document.getElementById("revealDescription");
    const deleteDescription = document.getElementById("deleteDescription");
    const deleteForm = document.getElementById("deleteForm");
    const copyPasswordBtn = document.getElementById("copyPasswordBtn");

    document.querySelectorAll("[data-close-modal]").forEach((button) => {
        button.addEventListener("click", () => {
            button.closest(".modal").classList.add("hidden");
        });
    });

    document.querySelectorAll(".reveal-btn").forEach((button) => {
        button.addEventListener("click", () => {
            revealEntryId.value = button.dataset.entryId;
            revealDescription.textContent = `Reveal the password stored for ${button.dataset.site}.`;
            revealedOutput.classList.add("hidden");
            revealedPassword.textContent = "";
            revealModal.classList.remove("hidden");
        });
    });

    document.querySelectorAll(".delete-btn").forEach((button) => {
        button.addEventListener("click", () => {
            deleteDescription.textContent = `Delete the credential for ${button.dataset.site}. This action cannot be undone.`;
            deleteForm.action = `/passwords/${button.dataset.entryId}/delete`;
            deleteModal.classList.remove("hidden");
        });
    });

    const revealForm = document.getElementById("revealForm");
    if (revealForm) {
        revealForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const entryId = revealEntryId.value;
            const formData = new FormData(revealForm);
            const response = await fetch(`/passwords/${entryId}/view`, {
                method: "POST",
                body: formData,
            });
            const data = await response.json();

            if (!data.ok) {
                alert(data.message);
                return;
            }

            revealedPassword.textContent = data.password;
            revealedOutput.classList.remove("hidden");
            document.getElementById("revealMasterPassword").value = "";
        });
    }

    if (copyPasswordBtn) {
        copyPasswordBtn.addEventListener("click", async () => {
            const copied = await copyWithTimeout(revealedPassword.textContent);
            if (copied) {
                copyPasswordBtn.textContent = "Copied";
                setTimeout(() => {
                    copyPasswordBtn.textContent = "Copy";
                }, 2500);
            }
        });
    }

    const generatorForm = document.getElementById("generatorForm");
    if (generatorForm) {
        const generatedPassword = document.getElementById("generatedPassword");
        const generatedStrengthBar = document.getElementById("generatedStrengthBar");
        const generatedStrengthLabel = document.getElementById("generatedStrengthLabel");
        const generatedEntropy = document.getElementById("generatedEntropy");
        const copyGeneratedBtn = document.getElementById("copyGeneratedBtn");

        generatorForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const formData = new FormData(generatorForm);
            const payload = {
                length: Number(formData.get("length")),
                use_uppercase: formData.get("use_uppercase") === "on",
                use_numbers: formData.get("use_numbers") === "on",
                use_symbols: formData.get("use_symbols") === "on",
            };

            const response = await fetch("/api/generate-password", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            const data = await response.json();

            if (!data.ok) {
                alert(data.message);
                return;
            }

            generatedPassword.textContent = data.password;
            setStrengthUI(generatedStrengthBar, generatedStrengthLabel, generatedEntropy, data.analysis);
        });

        copyGeneratedBtn.addEventListener("click", async () => {
            const copied = await copyWithTimeout(generatedPassword.textContent);
            if (copied) {
                copyGeneratedBtn.textContent = "Copied";
                setTimeout(() => {
                    copyGeneratedBtn.textContent = "Copy";
                }, 2500);
            }
        });
    }

    const strengthInput = document.getElementById("strengthPassword");
    if (strengthInput) {
        const strengthBar = document.getElementById("strengthBar");
        const strengthLabel = document.getElementById("strengthLabel");
        const entropyLabel = document.getElementById("entropyLabel");

        strengthInput.addEventListener("input", async () => {
            const response = await fetch("/api/analyze-password", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ password: strengthInput.value }),
            });
            const data = await response.json();
            setStrengthUI(strengthBar, strengthLabel, entropyLabel, data.analysis);
        });
    }
});
