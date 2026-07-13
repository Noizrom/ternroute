const form = document.querySelector("#prompt-form");
const promptInput = document.querySelector("#prompt");
const charCount = document.querySelector("#char-count");
const runButton = form.querySelector("button[type='submit']");
const statusTag = document.querySelector("#status-tag");
const answerCard = document.querySelector("#answer-card");
const answer = document.querySelector("#answer");
const errorMessage = document.querySelector("#error-message");
const stages = [...document.querySelectorAll(".trace li")];

const setStatus = (text, state = "") => {
  statusTag.textContent = text;
  statusTag.className = `status-tag ${state}`.trim();
};

const setStage = (index) => {
  stages.forEach((stage, stageIndex) => {
    stage.classList.toggle("complete", stageIndex < index);
    stage.classList.toggle("active", stageIndex === index);
  });
};

const describeContract = (spec) => {
  const details = [];
  if (spec.allowed_labels.length) details.push(spec.allowed_labels.join(" / "));
  if (spec.exact_sentences) details.push(`${spec.exact_sentences} sentences`);
  if (spec.max_words) details.push(`≤ ${spec.max_words} words`);
  if (spec.exact_bullets) details.push(`${spec.exact_bullets} bullets`);
  if (spec.code_only) details.push("code only");
  return details.length ? details.join(" · ") : spec.format;
};

const resetResult = () => {
  answerCard.hidden = true;
  errorMessage.hidden = true;
  stages.forEach((stage) => stage.classList.remove("active", "complete"));
  document.querySelector("#category-value").textContent = "Analyzing prompt";
  document.querySelector("#model-value").textContent = "Checking allowlist";
  document.querySelector("#contract-value").textContent = "Parsing constraints";
};

promptInput.addEventListener("input", () => {
  charCount.textContent = `${promptInput.value.length} / 4000`;
});
promptInput.dispatchEvent(new Event("input"));

document.querySelectorAll("[data-prompt]").forEach((button) => {
  button.addEventListener("click", () => {
    promptInput.value = button.dataset.prompt;
    promptInput.dispatchEvent(new Event("input"));
    promptInput.focus();
  });
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const prompt = promptInput.value.trim();
  if (!prompt) return;

  resetResult();
  setStatus("ROUTING", "running");
  setStage(0);
  runButton.disabled = true;
  runButton.querySelector("span").textContent = "Routing…";

  try {
    const response = await fetch("/api/route", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "The request failed.");

    document.querySelector("#category-value").textContent = data.category.replaceAll("_", " ");
    setStage(1);
    document.querySelector("#model-value").textContent = data.initial_model;
    await new Promise((resolve) => setTimeout(resolve, 180));
    setStage(2);
    document.querySelector("#contract-value").textContent = describeContract(data.output_spec);
    await new Promise((resolve) => setTimeout(resolve, 180));

    stages.forEach((stage) => {
      stage.classList.remove("active");
      stage.classList.add("complete");
    });
    answer.textContent = data.answer;
    answerCard.hidden = false;
    setStatus("COMPLETE", "done");
  } catch (error) {
    errorMessage.textContent = error instanceof Error ? error.message : "The request failed.";
    errorMessage.hidden = false;
    setStatus("FAILED", "failed");
  } finally {
    runButton.disabled = false;
    runButton.querySelector("span").textContent = "Route & run";
  }
});

document.querySelector("#copy-answer").addEventListener("click", async (event) => {
  await navigator.clipboard.writeText(answer.textContent);
  event.currentTarget.textContent = "Copied";
  setTimeout(() => { event.currentTarget.textContent = "Copy"; }, 1200);
});
