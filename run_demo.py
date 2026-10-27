import argparse
from pathlib import Path
from evidence import collect_http_samples
from agent import analyze
def main():
    p=argparse.ArgumentParser(); p.add_argument("--url",default="http://localhost:8080"); p.add_argument("--model",default=None); p.add_argument("--samples",type=int,default=30); a=p.parse_args()
    root=Path(__file__).resolve().parent; inp=root/"artifacts"/"input"; out=root/"artifacts"/"output"
    print("Saved",collect_http_samples(a.url,inp,a.samples)); print("Verified report:",analyze(inp,out,a.model))
if __name__=="__main__": main()
