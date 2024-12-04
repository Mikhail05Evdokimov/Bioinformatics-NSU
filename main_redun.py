import subprocess
from redun import task, File

@task()
def bwa(fastq, reference):
    subprocess.run(f"./bwa/bwa/bwa index {reference}", shell=True)
    subprocess.run(f"./bwa/bwa/bwa mem {reference} {fastq} | gzip -3 > aln-se.sam.gz", shell=True)
    return File("aln-se.sam.gz")


@task()
def samtools_view(bwa_file):
    subprocess.run(f"./samtools-1.21/samtools view -Sb {bwa_file.path} > aln-se.bam", shell=True)
    subprocess.run(f"./samtools-1.21/samtools sort aln-se.bam -o aln-se.sorted.bam", shell=True)
    return File("aln-se.sorted.bam")


@task()
def samtools_flagstat(view_file):
    subprocess.run(f"./samtools-1.21/samtools flagstat {view_file.path} > flagstat_report.txt", shell=True)
    return File("flagstat_report.txt")


@task()
def parse_percent(report):
    with open(report.path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            try:
                ind_start = line.index("mapped (") + 8
                ind_end = line[ind_start:].index("%") + ind_start
                with open("percent.txt", 'w+') as percent_file:
                    percent_file.write(line[ind_start:ind_end])
                break
            except Exception as e :
                print(e)

    return File("percent.txt")

@task()
def get_results(percent_file):
    with open(percent_file.path, 'r') as f:
        percent_value = float(f.read())

    if percent_value < 90:
        print("not OK")
        return "NO"
    else:
        print("OK")
        return "OK"

@task()
def main():
    fastqPath = "SRR31254081.fastq"
    referencePath = "GCA.fna"
    bwa_file = bwa(fastqPath, referencePath)
    view_file = samtools_view(bwa_file)
    report = samtools_flagstat(view_file)
    percent_file = parse_percent(report)
    res = get_results(percent_file)
    return res
