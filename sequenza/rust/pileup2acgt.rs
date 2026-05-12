// This file is part of sequenza-utils.
// SPDX-License-Identifier: GPL-3.0-only

use std::env;
use std::fs::File;
use std::io::{self, BufRead, BufReader, BufWriter, Read, Write};
use std::process;

#[derive(Clone, Copy)]
struct LastBase {
    index: usize,
    forward: bool,
}

fn count_base(
    base: u8,
    reference: u8,
    qual: u8,
    qlimit: u8,
    counts: &mut [i32; 4],
    strands: &mut [i32; 4],
) -> Option<LastBase> {
    if qual < qlimit {
        return None;
    }
    let normalized = match base {
        b'.' => reference,
        b',' => reference.to_ascii_lowercase(),
        other => other,
    };
    let (index, forward) = match normalized {
        b'A' => (0, true),
        b'C' => (1, true),
        b'G' => (2, true),
        b'T' => (3, true),
        b'a' => (0, false),
        b'c' => (1, false),
        b'g' => (2, false),
        b't' => (3, false),
        _ => return None,
    };
    counts[index] += 1;
    if forward {
        strands[index] += 1;
    }
    Some(LastBase { index, forward })
}

fn acgt(
    pileup: &[u8],
    quality: &[u8],
    reference: u8,
    qlimit: u8,
    noend: bool,
    nostart: bool,
) -> ([i32; 4], [i32; 4]) {
    let mut counts = [0i32; 4];
    let mut strands = [0i32; 4];
    let mut last_base: Option<LastBase> = None;
    let mut p = 0usize;
    let mut q = 0usize;

    while p < pileup.len() {
        match pileup[p] {
            b'$' => {
                if noend {
                    if let Some(last) = last_base {
                        counts[last.index] -= 1;
                        if last.forward {
                            strands[last.index] -= 1;
                        }
                    }
                }
                last_base = None;
                p += 1;
            }
            b'^' => {
                if p + 2 < pileup.len() {
                    if !nostart && q < quality.len() {
                        count_base(
                            pileup[p + 2],
                            reference,
                            quality[q],
                            qlimit,
                            &mut counts,
                            &mut strands,
                        );
                    }
                    q += 1;
                    p += 3;
                } else {
                    break;
                }
                last_base = None;
            }
            b'+' | b'-' => {
                p += 1;
                let len_start = p;
                while p < pileup.len() && pileup[p].is_ascii_digit() {
                    p += 1;
                }
                if len_start == p {
                    continue;
                }
                let len = std::str::from_utf8(&pileup[len_start..p])
                    .ok()
                    .and_then(|value| value.parse::<usize>().ok())
                    .unwrap_or(0);
                p = p.saturating_add(len).min(pileup.len());
            }
            b'.' | b',' | b'A' | b'C' | b'G' | b'T' | b'a' | b'c' | b'g' | b't' => {
                if q < quality.len() {
                    last_base = count_base(
                        pileup[p],
                        reference,
                        quality[q],
                        qlimit,
                        &mut counts,
                        &mut strands,
                    );
                } else {
                    last_base = None;
                }
                q += 1;
                p += 1;
            }
            _ => {
                q += 1;
                p += 1;
                last_base = None;
            }
        }
    }

    (counts, strands)
}

fn run(args: &[String]) -> io::Result<()> {
    if args.len() != 7 {
        eprintln!(
            "usage: {} <mpileup> <output> <min_depth> <qlimit> <noend:0|1> <nostart:0|1>",
            args[0]
        );
        process::exit(2);
    }

    let stdin = io::stdin();
    let stdout = io::stdout();
    let input: Box<dyn Read> = if args[1] == "-" {
        Box::new(stdin.lock())
    } else {
        Box::new(File::open(&args[1])?)
    };
    let output: Box<dyn Write> = if args[2] == "-" {
        Box::new(stdout.lock())
    } else {
        Box::new(File::create(&args[2])?)
    };
    let min_depth = args[3].parse::<i32>().unwrap_or(1);
    let qlimit = args[4].parse::<u8>().unwrap_or(53);
    let noend = args[5] == "1";
    let nostart = args[6] == "1";

    let reader = BufReader::new(input);
    let mut writer = BufWriter::new(output);
    writeln!(
        writer,
        "chr\tn_base\tref_base\tread.depth\tA\tC\tG\tT\tstrand"
    )?;

    for line in reader.lines() {
        let line = line?;
        let mut fields = line.split('\t');
        let chrom = match fields.next() {
            Some(value) => value,
            None => continue,
        };
        let position = match fields.next() {
            Some(value) => value,
            None => continue,
        };
        let reference = match fields.next() {
            Some(value) => value.as_bytes().first().copied().unwrap_or(b'N').to_ascii_uppercase(),
            None => continue,
        };
        let depth = match fields.next().and_then(|value| value.parse::<i32>().ok()) {
            Some(value) => value,
            None => continue,
        };
        let pileup = match fields.next() {
            Some(value) => value.as_bytes(),
            None => continue,
        };
        let quality = match fields.next() {
            Some(value) => value.as_bytes(),
            None => continue,
        };

        if depth >= min_depth && min_depth > 0 && reference != b'N' {
            let (counts, strands) = acgt(pileup, quality, reference, qlimit, noend, nostart);
            writeln!(
                writer,
                "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}:{}:{}:{}",
                chrom,
                position,
                reference as char,
                depth,
                counts[0],
                counts[1],
                counts[2],
                counts[3],
                strands[0],
                strands[1],
                strands[2],
                strands[3]
            )?;
        }
    }

    writer.flush()
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if let Err(error) = run(&args) {
        eprintln!("sequenza rust pileup2acgt failed: {}", error);
        process::exit(1);
    }
}
