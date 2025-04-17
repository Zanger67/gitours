from flask import Flask, send_file, jsonify, after_this_request
import dotenv
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from programs import helpers
from programs import itemizer
from programs import clone_summary as get_files
from programs.codetours import generate_codetour, parse_prompt_1


app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/retrieve/<path:repolink>')
def retrieve(repolink):
    dotenv.load_dotenv()

    try:
        cleaned_url = helpers.convert_git_url_to_cloner("https://" + repolink)
        print(f"Cleaned URL: {cleaned_url}")

        repo = itemizer.generate_repo_mappings(repo_url=cleaned_url, save_record=True)
        get_files.get_repo_json_tempfile(repo)
        git_file_json = repo.get_repo_json_data()

        cross_path = os.path.join(repo.get_mapping_path(), 'cross_reference.json')
        with open(cross_path, "r", encoding="utf-8") as f:
            cross_reference = json.load(f)

        llm_response_1 = get_files.summarize_with_llm_2(
            cross_ref_dict=cross_reference,
            repo_summary_dict=git_file_json
        )

        codetour_data = parse_prompt_1(data=llm_response_1)
        codetour = generate_codetour(data=codetour_data, repo=repo)
        
        output_path = os.path.join(repo.get_mapping_path(), 'codetour_output.tour')
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(codetour, f, indent=2)

        print(f"Codetour successfully written to: {output_path}")

        @after_this_request
        def cleanup(response):
            try:
                print("Cleaning up after request...")
                repo._close()
            except Exception as e:
                print("Cleanup error:", e)
            return response

        return send_file(output_path, mimetype='application/json', as_attachment=True)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)