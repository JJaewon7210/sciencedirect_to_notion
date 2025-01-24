def construct_prompt(article_content):
    """
    Constructs the prompt for the generative AI model.
    
    :param article_content: The content of the article to be summarized.
    :return: The formatted prompt string.
    """
    prompt = (
        "ARTICLE: \"\"\""
        f"{article_content}"
        "\"\"\"\n\n"
        "---\n\n"
        "## 1. Title\n\n"
        "Provide the full title of the article in English, exactly as it appears in the original.\n"
        "- DOI or URL: \n\n"
        "## 2. Authors\n\n"
        "List all authors in the order they appear, in English.\n\n"
        "## 3. Publication Date\n\n"
        "Provide the publication date in English, formatted as:\n"
        "**Month Day, Year** (e.g., January 15, 2023).\n"
        "- If only the year is provided, format as: **January 1, [Year]**.\n"
        "- If only the month and year are provided, format as: **[Month] 1, [Year]**.\n\n"
        "## 4. Journal\n\n"
        "Provide the name of the journal or publication in English.\n\n"
        "## 5. Keywords\n\n"
        "List 5-7 keywords that best represent the article's content in English. Use keywords directly from the article if available; otherwise, infer them from the content.\n\n"
        "- Keyword 1\n"
        "- Keyword 2\n"
        "- Keyword 3\n"
        "- Keyword 4\n"
        "- Keyword 5\n\n"
        "## 6. 초록 (Abstract)\n\n"
        "Summarize the abstract in 3-5 bullet points in Korean. Each point should be 1-2 sentences, covering:\n"
        "- Research background\n"
        "- Methods\n"
        "- Main results (include important numerical results where possible)\n"
        "- Conclusions\n"
        "- 첫 번째 요점\n"
        "- 두 번째 요점\n"
        "- 세 번째 요점\n\n"
        "## 7. 연구 격차 또는 문제 제기 (Research Gap or Problem Statement)\n\n"
        "In Korean, include the following:\n"
        "- 문제 제기 (Research gap or problem):\n"
            "    - Clearly state the limitations or issues in existing research.\n"
            "    - Describe the specific problem the study aims to address.\n"
        "- 중요성 (Significance):\n"
            "    - Explain why this research gap or problem is significant to the field.\n"
            "    - Highlight the impact of solving this problem.\n"
        "- 관련 연구 (Related previous studies):\n"
            "    - Mention 1-3 relevant studies and how they relate to the current research.\n"
            "    - Specify how the current research differs from or improves upon these studies.\n\n"
        "## 8. 연구 목적 (Objective)\n\n"
        "Clearly state the main objective(s) or research question(s) of the study in Korean. Include hypotheses if any. If there are multiple objectives, list them numerically.\n\n"
        "## 9. 연구 방법론 (Methodology)\n\n"
        "Provide a detailed description of the research methodology in Korean, including:\n"
        "- 연구 설계 (Research Design):\n"
            "    - Explain the overarching research design and its rationale.\n"
            "    - Specify any theoretical frameworks guiding the research.\n"
        "- 제안된 방법 (Proposed Methods):\n"
            "    - Detail each model or algorithm used in the study.\n"
            "    - Explain any novel techniques or features introduced to address the research problem.\n"
            "    - Clarify how each method or model was implemented.\n"
        "- 데이터셋 (Dataset):\n"
            "    - Describe the dataset(s) used, including the following:\n"
            "        - Data source (where it came from)\n"
            "        - Size of the dataset (number of samples, dimensions, etc.)\n"
            "        - Characteristics of the data (e.g., time-series, categories, variables)\n"
            "        - Data preprocessing steps (if any), such as normalization or filtering.\n\n"
        "## 10. 실험 (Experiment)\n\n"
        "Describe the experimental process and evaluation methods in Korean, including:\n"
        "- 실험 환경 (Experimental Setup):\n"
            "    - Detail the computational environment if available (e.g., hardware, software, configurations).\n"
            "    - Describe the conditions and parameters used in the experiments.\n"
        "- 평가 방법 (Evaluation Methods):\n"
            "    - List all evaluation metrics used and provide justifications for their selection.\n"
            "    - Metrics should align with the research objectives.\n"
            "    - Provide a brief explanation of how each metric measures performance (e.g., MSE).\n"
        "- 비교 분석 (Comparative Analysis):\n"
            "    - Describe any baseline methods or models used for comparison.\n"
            "    - Explain any ablation studies conducted to assess the impact of specific components.\n"
            "    - Highlight how the proposed methods improve upon the baselines.\n\n"
        "## 11. 연구 결과 및 토의 (Results and Discussions)\n\n"
        "Present key findings and their interpretations in bullet points in Korean, including:\n"
        "- 주요 결과 (Main Results):\n"
            "    - Provide the first major result, including important numerical results.\n"
            "    - Provide the second major result.\n"
            "    - Provide any additional major results.\n"
        "- 결과 해석 (Interpretation of Results):\n"
            "    - Explain the meaning of the first major result.\n"
            "    - Explain the second major result.\n"
            "    - Compare or interpret any additional results.\n"
        "- 시사점 (Implications):\n"
            "    - Explain the theoretical and practical implications of the study's findings.\n"
            "    - Discuss how the results contribute to solving the research problem or advancing the field.\n"
            "    - Provide examples of how these findings might be applied in real-world scenarios.\n"
        "- 한계점 (Limitations):\n"
            "    - Identify any limitations or potential biases in the study’s methodology or data.\n"
            "    - Discuss how these limitations may affect the generalizability or validity of the results.\n"
            "    - Suggest areas for improvement or additional factors to consider in future research.\n\n"
        "## 12. 연구의 기여 (Contribution)\n\n"
        "In Korean, include the following:\n"
        "- 주요 기여점 (Main Contributions):\n"
            "    - Detail the primary contributions of the study to the academic field or practical applications.\n"
            "    - Highlight any new insights, methods, or frameworks introduced by the study.\n"
        "- 연구 격차 해결 (Addressing Research Gap/Problem):\n"
            "    - Describe specifically how the study addresses the research gap or problem highlighted in Section 7.\n"
            "    - Clarify what this research contributes that previous studies did not.\n"
        "- 시사점과 적용성 (Implications and Applications):\n"
            "    - Discuss the theoretical implications of the results.\n"
            "    - Provide suggestions for practical applications, such as industry practices or policy changes.\n"
        "- 한계점 및 향후 연구 (Limitations and Future Research):\n"
            "    - Point out any unresolved issues or limitations in the current study.\n"
            "    - Propose potential future research directions, including improvements in methodology, broader dataset applications, or exploring new research questions.\n"
    )
    return prompt


def construct_response_schema():
    return {
        "type": "OBJECT",
        "required": [
            "Title",
            "Authors",
            "Publication Date",
            "Journal",
            "Keywords",
            "Abstract",
            "Research Gap Or Problem Statement",
            "Objective",
            "Methodology",
            "Experiment",
            "Results And Discussions",
            "Contribution",
        ],
        "properties": {
            "Title": {"type": "STRING"},
            "DOI or URL": {"type": "STRING"},
            "Authors": {"type": "ARRAY", "items": {"type": "STRING"}},
            "Publication Date": {"type": "STRING"},
            "Journal": {"type": "STRING"},
            "Keywords": {"type": "ARRAY", "items": {"type": "STRING"}},
            "Abstract": {"type": "ARRAY", "items": {"type": "STRING"}},
            "Research Gap Or Problem Statement": {
                "type": "OBJECT",
                "required": ["Research Gap", "Significance", "Related Studies"],
                "properties": {
                    "Research Gap": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "Significance": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "Related Studies": {"type": "ARRAY", "items": {"type": "STRING"}},
                },
            },
            "Objective": {"type": "ARRAY", "items": {"type": "STRING"}},
            "Methodology": {
                "type": "OBJECT",
                "required": ["Research Design", "Proposed Methods", "Dataset"],
                "properties": {
                    "Research Design": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "Proposed Methods": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "Dataset": {
                        "type": "OBJECT",
                        "required": [
                            "Source",
                            "Size",
                            "Characteristics",
                            "Preprocessing Steps",
                        ],
                        "properties": {
                            "Source": {"type": "ARRAY", "items": {"type": "STRING"}},
                            "Size": {"type": "ARRAY", "items": {"type": "STRING"}},
                            "Characteristics": {"type": "ARRAY", "items": {"type": "STRING"}},
                            "Preprocessing Steps": {"type": "ARRAY", "items": {"type": "STRING"}},
                        },
                    },
                },
            },
            "Experiment": {
                "type": "OBJECT",
                "required": [
                    "Experimental Setup",
                    "Evaluation Methods",
                    "Comparative Analysis",
                ],
                "properties": {
                    "Experimental Setup": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "Evaluation Methods": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "Comparative Analysis": {"type": "ARRAY", "items": {"type": "STRING"}},
                },
            },
            "Results And Discussions": {
                "type": "OBJECT",
                "required": [
                    "Main Results",
                    "Result Interpretations",
                    "Implications",
                    "Limitations",
                ],
                "properties": {
                    "Main Results": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "Result Interpretations": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "Implications": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "Limitations": {"type": "ARRAY", "items": {"type": "STRING"}},
                },
            },
            "Contribution": {
                "type": "OBJECT",
                "required": [
                    "Main Contributions",
                    "Addressing Research Gap",
                    "Implications And Applications",
                    "Limitations And Future Research",
                ],
                "properties": {
                    "Main Contributions": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "Addressing Research Gap": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "Implications And Applications": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "Limitations And Future Research": {"type": "ARRAY", "items": {"type": "STRING"}},
                },
            },
        }
    }


def construct_system_instruction():
    return """You are a research assistant tasked with summarizing academic articles. Your goal is to extract key information from the articles and present it in a structured format."""
