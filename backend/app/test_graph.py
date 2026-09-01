# Import our complete Knowledge Integrity workflow.
from .graph import knowledge_graph


# Create a test question that should be answered from our indexed knowledge.
question = "Who should own internal engineering documentation?"


# Send the question through the complete LangGraph workflow.
result = knowledge_graph.invoke({
    "question": question
})


# Print the final answer generated after retrieval and verification.
print("\n===== FINAL ANSWER =====")
print(result.get("answer", "No answer generated."))


# Print the verification result so we can inspect how the knowledge was checked.
print("\n===== VERIFICATION =====")
print(result.get("verification", {}))


# Print the retrieved evidence so we can confirm Qdrant actually supplied
# the knowledge used by the workflow.
print("\n===== RETRIEVED EVIDENCE =====")
for item in result.get("results", []):
    print(item)