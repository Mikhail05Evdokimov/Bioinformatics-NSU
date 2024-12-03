import subprocess
from redun import task, File

@task()
def bwa(fastq, reference):
    subprocess.run(f"./bwa/bwa/bwa index {reference}", shell=True)
    subprocess.run(f"./bwa/bwa/bwa mem {reference} {fastq} | gzip -3 > aln-se.sam.gz", shell=True)


@task()
def samtools_view():
    subprocess.run(f"./samtools-1.21/samtools view -Sb aln-se.sam.gz > aln-se.bam", shell=True)
    subprocess.run(f"./samtools-1.21/samtools sort aln-se.bam -o aln-se.sorted.bam", shell=True)


@task()
def samtools_flagstat():
    subprocess.run(f"./samtools-1.21/samtools flagstat aln-se.sorted.bam > flagstat_report.txt", shell=True)
    return File("flagstat_report.txt")


@task()
def parse_percent(report):
    with open(report.path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            try:
		ind_start = line.index("mapped (") + 8
		ind_end = line[ind_start:].index
                with open("percent.txt", 'w+') as percent_file:
                    percent_file.write(line[ind_start:ind_end])
		break
	    except Exception :
		pass

    return File("percent.txt")

@task()
def get_results():
    with open("percent_txt", 'r') as f:
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
    bwa(fastqPath, referencePath)
    samtools_view()
    report = samtools_flagstat()
    parse_percent(report)
    res = get_results()
    return res
