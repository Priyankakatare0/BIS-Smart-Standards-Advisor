import gradio as gr
from src.pipeline  import run_pipeline
from src.retriever import preload as preload_retriever
from src.reranker  import preload as preload_reranker

# Warm up all models so first user query isn't slow
print("Warming up models...")
preload_retriever()
preload_reranker()
print("Ready.")

EXAMPLES = [
    "53 grade ordinary portland cement for structural concrete work",
    "TMT steel reinforcement bars for RCC construction",
    "coarse crushed stone aggregate for road base and concrete",
    "fly ash bricks for load bearing masonry wall construction",
    "precast reinforced concrete pipes for underground stormwater drainage",
]

def predict(product_description: str):
    if not product_description.strip():
        return "Please enter a product description.", "", ""

    try:
        recs, latency = run_pipeline(product_description.strip())
    except Exception as e:
        return f"Error: {e}", "", ""

    if not recs:
        return "No matching standards found. Try a more specific description.", "", ""



    # Format markdown output with colored confidence score
    md = ""
    for i, r in enumerate(recs, 1):
        score = r.get("rerank_score")
        if score is not None:
            if score >= 2:
                color = "#27ae60"  # green
            elif score >= 0:
                color = "#e67e22"  # orange
            else:
                color = "#c0392b"  # red
            score_str = f' <span style="color:{color}; font-weight:bold">(Confidence: {score:.3f})</span>'
        else:
            score_str = ""
        md += f"### {i}. {r['standard_id']}{score_str}\n"
        md += f"{r['rationale']}\n\n"
        md += "---\n"

    ids_list  = ", ".join(r["standard_id"] for r in recs)
    latency_s = f"Completed in {latency}s"

    return md, ids_list, latency_s

# Build UI
with gr.Blocks(title="BIS Standards Recommendation Engine") as demo:
    gr.Markdown("""
# BIS Standards Recommendation Engine
**Helping Indian MSEs find the right BIS standards instantly**
Enter a building material product description to get the most relevant standards from SP 21.
""")

    with gr.Row():
        with gr.Column(scale=2):
            inp = gr.Textbox(
                label="Product Description",
                placeholder="e.g. ordinary portland cement 53 grade for structural use",
                lines=3,
            )
            with gr.Row():
                btn   = gr.Button("Find Standards", variant="primary")
                clear = gr.Button("Clear")

            gr.Examples(examples=EXAMPLES, inputs=inp,
                        label="Click an example to try")

        with gr.Column(scale=3):
            lat_out = gr.Markdown("")
            res_out = gr.Markdown(label="Recommended BIS Standards")
            ids_out = gr.Textbox(label="Standard IDs", interactive=False,
                                 info="Copy these IDs for your records")

    btn.click(fn=predict, inputs=inp, outputs=[res_out, ids_out, lat_out])
    inp.submit(fn=predict, inputs=inp, outputs=[res_out, ids_out, lat_out])
    clear.click(fn=lambda: ("","",""), outputs=[res_out, ids_out, lat_out])

if __name__ == "__main__":
    demo.launch(share=False, server_port=7860)