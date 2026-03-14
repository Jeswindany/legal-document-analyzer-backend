# Legal Clause Classification using Legal-BERT (LEDGAR Dataset)

This project fine-tunes **Legal-BERT** for **legal contract clause classification** using the **LEDGAR dataset** from the LexGLUE benchmark.

The model classifies legal clauses into **100 contract categories** such as:

- Confidentiality
- Indemnification
- Governing Laws
- Arbitration
- Termination
- Intellectual Property
- Payments
- Benefits
- and many more.

---

## Project Overview

Legal contracts contain structured clauses describing obligations, rights, and procedures. Automatically identifying clause types can assist in:

- Contract analysis
- Legal document automation
- Compliance monitoring
- Contract search and retrieval
- Legal AI assistants

This project fine-tunes **Legal-BERT (`nlpaueb/legal-bert-base-uncased`)** on the **LEDGAR dataset**.

---

## Dataset

Dataset used:

- **LEDGAR (LexGLUE Benchmark)**

Source:

- HuggingFace Datasets: `lex_glue/ledgar`

Dataset statistics:

| Split      | Samples |
| ---------- | ------- |
| Train      | 60,000  |
| Validation | 10,000  |
| Test       | 10,000  |

## Total labels: **100 clause types**

## Example labels:

- Confidentiality
- Indemnifications
- Governing Laws
- Termination
- Payments
- Notices
- Representations
- Intellectual Property
- Arbitration
- Compliance With Laws

---

## Model

Base model: nlpaueb/legal-bert-base-uncased

Legal-BERT is pre-trained on:

- Legal contracts
- Legislation
- Court decisions

This improves performance on legal NLP tasks compared to general BERT models.

---

## Model Architecture

```
Legal-BERT Base
↓
CLS Token Representation
↓
Linear Classification Layer
↓
100 Output Labels
```

Max sequence length: 512 tokens

---

## Training Configuration

Training was done using **HuggingFace Trainer**.

### Hyperparameters

| Parameter       | Value      |
| --------------- | ---------- |
| Epochs          | 5          |
| Batch Size      | 8          |
| Learning Rate   | 2e-5       |
| Max Length      | 512        |
| Optimizer       | AdamW      |
| Mixed Precision | FP16       |
| Evaluation      | Each epoch |

---

## Training Results

| Epoch | Validation Accuracy | Macro F1   | Micro F1   |
| ----- | ------------------- | ---------- | ---------- |
| 1     | 0.8458              | 0.7463     | 0.8458     |
| 2     | 0.8646              | 0.7822     | 0.8646     |
| 3     | 0.8735              | 0.7965     | 0.8735     |
| 4     | 0.8799              | 0.8088     | 0.8799     |
| 5     | **0.8820**          | **0.8097** | **0.8820** |

Final model performance:

```
Accuracy: 88.2%
Macro F1: 0.81
Micro F1: 0.88
```

---

# Usage

Install dependencies:

```bash
pip install transformers torch
```

Load Model:

```py
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model_name = "jeswinpauldany/legalbert-clause-classifier"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

text = "The parties agree to maintain confidentiality of proprietary information."

inputs = tokenizer(text, return_tensors="pt", truncation=True)

outputs = model(**inputs)
prediction = torch.argmax(outputs.logits)

print(model.config.id2label[prediction.item()])
```

---
