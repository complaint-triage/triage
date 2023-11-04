from dotenv import load_dotenv
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jsonrpc import JSONRPC
from werkzeug.security import safe_join

import os
from llm import Generator, Stage1, Stage2

production: bool = False
static_path: str = '../frontend/dist'
app: Flask
jsonrpc: JSONRPC


class Pathway:
    def __init__(self, id: str, name: str, descr: str, file: str):
        self.id = id
        self.name = name
        self.desc = descr
        self.file = file


data_dir: str ='pathways'
pathways: list[Pathway] = {
    Pathway('ads_standards', 'Ad Standards', 'Australia\'s advertising regulator', 'Ad Standards.txt'),
    Pathway('anti_discrimination', 'Anti-Discriminiation NSW', 'The New South Wales state government body that administers the Anti-Discrimination Act', 'Anti-Discrimination NSW.txt'),
    Pathway('acma', 'Australian Communications and Media Authority', 'ACMA regulate communications and media services in Australia', 'Australian Communications and Media Authority.txt'),
    Pathway('afp', 'Australian Federal Police', 'Australia\'s national policing agency', 'Australian Federal Police (AFP) - Federal.txt'),
    Pathway('fwc', 'Fair Work Commission', 'Australia\'s workplace relations tribunal and registered organisations regulator', 'Fair Work Commission.txt'),
    Pathway('fwo', 'Fair Work Ombudsman', 'FWO promote harmonious, productive, cooperative and compliant workplace relations in Australia', 'Fair Work Ombudsman.txt'),
    Pathway('fcfca', 'Federal Circuit and Family Court of Australia', 'The Federal Circuit and Family Court of Australia', 'Federal Circuit and Family Court of Australia.txt'),
    Pathway('fca', 'Federal Court of Australia', 'The FCA decides disputes according to law', 'Federal Court of Australia.txt'),
    Pathway('icac', 'Independent Commission Against Corruption', 'The ICAC helps NSW public sector agencies and individuals prevent corruption', 'Independent Commission Against Corruption (ICAC).txt'),
    Pathway('jcnsw', 'Judical Commission of NSW', 'The Judical Commission of NSW provides sentencing information and continuing education to and examines complaints made against judicial officers', 'Judicial Commission of NSW.txt'),
    Pathway('lecc', 'Law Enforcement Conduct Commission', 'The Law Enforcement Conduct Commission is responsible for investigating allegations of serious misconduct by the NSW Police Force and NSW Crime Commission', 'Law Enforcement Conduct Commission (LECC) - NSW.txt'),
    Pathway('nacc', 'National Anti-Corruption Commission', 'The NACC has the power to investigate Commonwealth ministers, public servants, statutory office holders, government agencies, parliamentarians, and personal staff of politicians', 'NACC - Federal.txt'),
    Pathway('ndis', 'NDIS Quality and Safeguard Commission', 'The NDIS Commission works with participants and providers to improve the quality and safety of NDIS services and supports', 'NDIS Quality and Safeguard Commission.txt'),
    Pathway('nswo', 'NSW Ombudsman', 'The NSW Ombudsman is an independent agency who assists when a dispute arises between individuals and industry bodies or government agencies', 'NSW Ombudsman.txt'),
    Pathway('nswpf', 'NSW Police Force', 'The New South Wales Police Force is a law enforcement agency of New South Wales', 'NSW Police Force.txt'),
    Pathway('olsc', 'Office of the NSW Legal Services Commissioner', 'The Office of the NSW Legal Services Commissioner is an independent statutory body that deals with complaints about lawyers', 'Office of the Legal Services Commissioner.txt'),
    Pathway('rch', 'Registrar of Community Housing', 'The Registrar of Community Housing is responsible for registering, monitoring and regulating community housing providers in NSW', 'Registrar of Community Housing.txt'),
    Pathway('swnsw', 'SafeWork NSW', 'SafeWork NSW promotes productive, healthy and safe workplaces for workers and employers in New South Wales', 'SafeWork NSW.txt'),
}

pathway_map = dict([(pathway.id, pathway) for pathway in pathways])

def init_app():
    global app
    global jsonrpc

    load_dotenv('setting.env')
    load_dotenv('secret.env')

    app = Flask(__name__)
    jsonrpc = JSONRPC(app, '/t/rpc', enable_web_browsable_api=not production)
    deployment = os.getenv('AZURE_DEPLOYMENT')
    deployment_gpt4 = os.getenv('AZURE_DEPLOYMENT_GPT4')
    stage1: Stage1 = Stage1(deployment_gpt4)
    stage2: Stage2 = Stage2(deployment_gpt4)
    generator: Generator = Generator(deployment_gpt4) 
    if not production:
        CORS(app)

        @app.route('/<path:path>')
        @app.route('/', defaults={'path': ''})
        def static_files(path: str):
            # handle the index.html case
            if os.path.isdir(safe_join(static_path, path)):
                path = safe_join(path, 'index.html')
            return send_from_directory(static_path, path)

        @jsonrpc.method('ping')
        def rpc_ping() -> str:
            return 'gnip'

    @jsonrpc.method('submit')
    def rpc_submit(complaint: str) -> dict:
        response = stage1.query(complaint)
        return {'complaint': complaint, 'response': response}
    
    def stage2_query(complaint: str, id: str, pathway_file: str) -> tuple:
        with open(pathway_file) as f:
            detailed = f.read()
        return stage2.query(complaint, id, detailed)
    
    def stage2_filter(complaint: str, pathway_ids: list[str]) -> list[tuple]:
        filtered: list[tuple] = []
        for id in pathway_ids:
            if id in pathway_map:
                print(f'id {id} pathwaymap {pathway_map[id]}')
                valid, reason = stage2_query(complaint, id, os.path.join(data_dir, pathway_map[id].file))
                filtered.append((id, valid, reason))
        return filtered

    @jsonrpc.method('stage2_submit')
    def query_all(complaint: str) -> list[dict]:
        matches = stage1.query(complaint)
        results = stage2_filter(complaint, matches)
        json_results = [{'id': id,
                         'name': pathway_map[id].name,
                         'descr': pathway_map[id].desc,
                         'valid': valid,
                         'reason': reason} for (id, valid, reason) in results if valid]
        return json_results
    
    @jsonrpc.method('generate')
    def generate_output(complaint: str, id: str) -> dict:
        results = generator.generate(complaint, id)
        json_results = {'output': results}
        return json_results

init_app()
