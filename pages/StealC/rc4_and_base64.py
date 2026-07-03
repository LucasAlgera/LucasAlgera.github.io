### RC4 Decryption script is from @hsauers5 on GitHub
### https://gist.github.com/hsauers5/491f9dde975f1eaa97103427eda50071.

import base64

def key_scheduling(key):
    sched = [i for i in range(256)]

    i = 0
    for j in range(256):
        i = (i + sched[j] + key[j % len(key)]) % 256

        sched[j], sched[i] = sched[i], sched[j]

    return sched


def stream_generation(sched):
    i = 0
    j = 0

    while True:
        i = (i + 1) % 256
        j = (j + sched[i]) % 256

        sched[i], sched[j] = sched[j], sched[i]

        yield sched[(sched[i] + sched[j]) % 256]


def rc4_bytes(data, key):
    """
    RC4 operating directly on bytes.
    """
    key_bytes = [ord(c) for c in key]

    sched = key_scheduling(key_bytes)
    keystream = stream_generation(sched)

    return bytes(b ^ next(keystream) for b in data)


def decode_string(encoded_b64, key):
    ciphertext = base64.b64decode(encoded_b64)
    plaintext = rc4_bytes(ciphertext, key)

    return plaintext


if __name__ == "__main__":

    encoded = [
        "NhMKouq0UhO8+yrqBbMshho1cK9UXw==",
        "cVZIsOCpTxu89WLvBbYzhB1gaK4GQWdB4w==",
        "OQMXorzuDgzhoWg=",
        "PRUHoqSoTwzhoWg=",
        "OQMX4eK1GU7p",
        "LBQKoKT2GlCrqWi0",
        "MQsb4eK1GU7p",
        "KQ4QuqTvDQzhoWg=",
        "KxQboOOpU0bpoQ==",
        "LQ8SpbHrFAzhoWg=",
        "LQ8bvryoTwzhoWg=",
        "MBMavry1GU7p",
        "GQMXopf+CWvorGO9dexh2E5nLO00Bm1M",
        "GQMXopf+CWvorGO9dexh2E5nLO0=",
        "GQMXopPpGEPxqEaxRO9jx2xwMfMvLV593mz0",
        "GQMXorzuDnHxrHasRfI=",
        "GQMXorzuDnHtuHC8X/Vs",
        "GQMXooP6C0fMoGW/VdZt5F5wO/8K",
        "GQMXopTyDlLqvmGRXeNl0g==",
        "DAIZg6X+D1vTrGitVcd69g==",
        "DAIZl77uEGngtEGgcQ==",
        "DAIZg6X+D1vTrGitVcd64A==",
        "DAIZnaD+E2ngtEGgZw==",
        "DAIZkbz0DkfOqH0=",
        "HQgQpLXpCXHxv222V9Fn1F9wN+oeK3Ja8F/NrpbDLgun/2DNGZNlWLAbZ2XfC78EzwCtkw==",
        "DAIZnaD+E2ngtEGgcQ==",
        "HRUHoqTOE1L3onC9U/ZG1l5j",
        "HRUHoqTICVDso2OMX8Br2UtwJ98=",
        "HRUHoqTZFEzkv32MX9F2xUNsOd8=",
        "HRUbs6T+Pk3ovWWsWeBu0mhrKvMGHw==",
        "DQISt7PvMkDvqGes",
        "HRUbs6T+Pk3ovWWsWeBu0m5B",
        "GgISt6T+OWE=",
        "GgISt6T+MkDvqGes",
        "HA4KkLzv",
        "DAo5t6TXFFHx",
        "DAost7fyDlbgv1a9Q+13xUlnLQ==",
        "DAotprHpCXHgvnexX+w=",
        "DAo7vLTIGFH2pGu2",
        "HRUbs6T+Llb3qGW1f+xK8EZtPP8L",
        "GQIKganoCUfogGGsQuthxA==",
        "GQIKlpM=",
        "DAISt7HoGGbG",
        "GQIKmbXiH03kv2CUUfttwl5ON+0T",
        "GwkLv5TyDlLprH2cVfRr1E9xCQ==",
        "GwkLv5TyDlLprH2LVfZ23kRlLck=",
        "KRQOoLn1CUTE",
        "DgYKup36CUHtnnS9U8M=",
        "DRMMkb3rPmM=",
        "DQ8bvrzeBUfmuHC9dfpD",
        "DS85t6TdEk7hqHaIUfZq9g==",
        "GA4QtpbyD1Hxi220VcM=",
        "GA4Qtp7+BVbDpGi9cQ==",
        "GA4QtpP3ElHg",
        "MhQKoLP6CWM=",
        "HQgOq5byEUfE",
        "GgISt6T+O0vpqEU=",
        "CRUXprXdFE7g",
        "HRUbs6T+O0vpqFM=",
        "DAIftpbyEUc=",
        "GQIKlLn3GHHst2GdSA==",
        "HRUbs6T+M0PoqGCIWfJn9g==",
        "MhQKoLz+E2M=",
        "GQIKl77tFFDqo2m9XvZU1lhrP/wLClY=",
        "Eggds7zaEU7qrg==",
        "Eggds7zdD0fg",
        "DAITvab+OUv3qGesX/B79g==",
        "DQIKl77tFFDqo2m9XvZU1lhrP/wLClY=",
        "HRUbs6T+OUv3qGesX/B79g==",
        "GQIKkaXpD0fruVSqX+FnxFlLOg==",
        "GQIKh6P+D2bgq2WtXPZO2EljMvspDnpM",
        "GQIKganoCUfonWuvVfBRw0t2K+0=",
        "GQIKnr/4HE7ghGq+X9U=",
        "GQIKhL/3CE/ghGq+X/Bv1l5rMfAm",
        "GQIKhbn1GU3yvkCxQudhw0VwJ98=",
        "HRUbs6T+KU3qoWy9XPIxhXlsP+4UB3hd",
        "GQIKhrn2GHjqo2GRXuRtxUdjKvcIAQ==",
        "GQIKnrHoCWf3v2uq",
        "GQIKnr/8FEHkoVSqX+FnxFltLNcJCXhb/kzQt43CGSc=",
        "DhURsbXoDhG3g2GgRNU=",
        "DhURsbXoDhG3i22qQ/ZV",
        "GQIKganoCUfohGq+Xw==",
        "GQIKnr/4HE7RpGm9",
        "GQsRsLH3MEfoonahY/Zjw19xG+Y=",
        "CRUXprXLD03mqHerfedv2Fh7",
        "CQYXppb0D3Hso2O0Vc1g3U9hKg==",
        "DAINp73+KUr3qGW8",
        "DxIbp7XODkf3jFSb",
        "CA4MpqX6EWPpoWu7dfo=",
        "CA4MpqX6EWT3qGGdSA==",
        "HRUbs6T+LVDqrmGrQ8M=",
        "HQYQsbX3NE0=",
        "FgIfopbpGEc=",
        "CgIMv7n1HFbgnXa3U+dxxA==",
        "FVRMlbXvME3huGi9dutu0mRjM/siF0A=",
        "ERcbvIDpEkHgvnc=",
        "GQIKlLn3GGPxuXaxUvd20llD",
        "DAINt6TeC0fruQ==",
        "FgIfopH3EU3m",
        "DAIftpTyD0fmuWuqScFq1kRlO+0w",
        "GQIKlLn3GHHst2E=",
        "GQIKgqL0Hkf2vky9UfI=",
        "CQ4at5PzHFDRokmtXPZr9VN2Ow==",
        "GQIKganoCUfomW21VQ==",
        "DBMSlbXvK0f3vm23Xg==",
        "KQYSvrXvDg==",
        "OA4St6M=",
        "LQgYpg==",
        "HV0igqL0GlDkoEC5RONe",
        "HQgQprX1CQ/RtHS9CqJjx1puN/0GG35G/QLOrY3CAC2Uwg==",
        "Digthg==",
        "MRcdvbT+",
        "OgYKsw==",
        "OA4St776EEc=",
        "KxcSvbH/IkTsoWE=",
        "MRQhsaLiDVY=",
        "OwkdoKnrCUfhkm+9SQ==",
        "NQIHoQ==",
        "KFZO/KTjCQ==",
        "KFVO/KTjCQ==",
        "EAIKpb/pFg==",
        "HQgRubn+Dg==",
        "EggZu767OUPxrA==",
        "CQIc8pT6CUM=",
        "Fg4Npr/pBA==",
        "PBURpaP+D1E=",
        "LgsLtbn1Dg==",
        "Eggds7y7OFrxqGqrWe1sl3lnKuoOAXBa",
        "DR4QsfDeBVbgo3exX+wi5E92KvcJCGQ=",
        "Fwkat6j+GWbH",
        "HTIsgJXVKQ==",
        "PQ8Mvb3+Ikf9uWG2Q+tt2XU=",
        "AVchu77/GFrgqWC6b+5nwU9uOvw=",
        "Eggds7y7LlbkuWE=",
        "Gl1Wk+ugOmO+9j+PdKs=",
        "DiYqmg==",
        "MBQN4f7/EU4=",
        "EDQtjZn1FFY=",
        "EDQtjYPzCFbhonO2",
        "DixP44/cGFbMo3C9Quxj22FnJ80LAGM=",
        "DixP44/dD0fgnmi3RA==",
        "DixP44/aCFbtqGqsWeFjw08=",
        "DixP44PfL33BqGeqSfJ2",
        "MggZu77oU0j2omo=",
        "MggZu77o",
        "NggNpr76EEc=",
        "OwkdoKnrCUfhmHe9Quxj2k8=",
        "OwkdoKnrCUfhnWWrQ/VtxU4=",
        "LgYNoaf0D0b243CgRA==",
        "PBURpaP+Dxil",
        "LhURtLn3GBil",
        "KxUS6PA=",
        "MggZu76hXQ==",
        "LgYNoaf0D0a/7Q==",
        "PQgRubn+Dgz2vGixROc=",
        "OAgMv7jyDlbqv332Q/Nu3l5n",
        "LgsfsbXoU1H0oW2sVQ==",
        "LhURtLn3GFGrpGqx",
        "CjUrlw==",
        "GCYygZU=",
        "FiYslofaL2fZiUGLc9BL535LEdA7PG5a50jJgqHJMiu6zWn+Ho5vSbosbWTgSQ==",
        "DhURsbXoDk33g2W1VdF2xUNsOQ==",
        "bkc5kA==",
        "fiA8",
        "DSg4hofaL2fZgG27Qu1x2Ex2AskOAXNG5F74nZfeLjqm2FPLHpJlQ6cDV3jVF6UA2gOz",
        "Gg4Norz6BGzkoGE=",
        "Gg4Norz6BHTgv3exX+w=",
        "MAYTtw==",
        "LgYKug==",
        "LQgYpo/rHFbt",
        "KxQbjaapTQ==",
        "Kh4Otw==",
        "LgYMobXEHk3qpm29Qw==",
        "LgYMobXEEU3ipGqr",
        "LgYMobXEFUv2uWuqSQ==",
        "LgYMobXECkfnqWWsUQ==",
        "KggVt74=",
        "OBURv4/3EkHkoQ==",
        "OBURv4/oBEzm",
        "OBURv4/SE0bgtWG8dMA=",
        "PRQXtrw=",
        "LRMfoKTEDUPxpQ==",
        "MwYNuaM=",
        "LAIdp6LoFFTg",
        "MwYGjaPyB0c=",
        "NxMboLHvFE3rvg==",
        "LRIdsbXoDg==",
        "PwQdt6PoIlbqpmG2",
        "LQIStI//GE7guWE=",
        "KgYVt4/oHlDgqGqrWO12",
        "MggftrXp",
        "LRMbs7zEDlbgrGk=",
        "LRMbs7zEElfxoWu3Ww==",
        "PAsRsbv+GQ==",
        "KxUS",
        "LBIQjbHoIkPhoG22",
        "PRUbs6T+",
        "NhAXtg==",
        "PBIXvrQ=",
        "OggQtw==",
        "EAIKpb/pFgLMo2K3Cg==",
        "V0pem4ChXWvV8g==",
        "V0pekb/uE1b3tD74edFNiHZsAvA0FmRd9kCEjZfBMT661T8=",
        "V0pemofSORil",
        "V0penYOhXQ==",
        "CwkVvL/sEw==",
        "fk88p7n3GQI=",
        "V0pek6L4FUvxqGesRfBnjQp6aKo=",
        "V0peh6P+D2zkoGHiEA==",
        "V0pekb/2DVfxqHb4fuNv0hAi",
        "V0penr/4HE6lmW21Vbgi",
        "V0peh4TYRwI=",
        "V0penrH1GlfkqmHiEA==",
        "V0pembXiH03kv2CrCqI=",
        "V0penrHrCU319yQ=",
        "V0pegKX1E0vrqiSIUfZqjQo=",
        "V0pekYDORwI=",
        "V0pekb/pGFG/7Q==",
        "V0pehrjpGEPhvj74",
        "V0pegJHWRwI=",
        "V0pelrnoDU7ktCSKVfFt2192N/EJVTc=",
        "V24zvb7yCU337Q==",
        "V253lrXtFEHg7Uq5Xec4lw==",
        "V253lrXtFEHg7VesQuts0BAi",
        "V253gLXoEk7wuW23Xrgi",
        "V253kb/3ElCliWGoROo4lw==",
        "fgUXpqO7DUf37XSxSOdu",
        "V0pelYDORw==",
        "DhURsbXoDgLmonG2RLgi",
        "DhURsbXoDgLJpHesCqI=",
        "GxUMvaK7GVfovW22V6JyxUVhPfsUHDdF+l7Q",
        "FwkNprH3EUfh7UWoQPE4",
        "HwsS8oXoGFD29w==",
        "HRIMoLX1CQLQvmGqCg==",
        "LR4NprX2Ikvrq2v2RPp2",
        "cAIGtw==",
        "LBIQs6M=",
        "cwkRovC2HgI=",
        "cAoNuw==",
        "cRcfoaPyC0c=",
        "LQQMt7X1DkrquSqyQOU=",
        "DQgYpqf6D0fZm2W0Rude5F5nP/M=",
        "DRMbs73LHFbt",
        "AgQRvLbyGn4=",
        "DRMbs70=",
        "HyU9lpXdOmrMh0+UfcxN53tQDcoyOUBxynfFvIHIOTmvxGzEB41hQqYvc2TPDaMCzBemqL9w22DyZwj4D+98hg==",
        "PwUdtrX9Gkrsp2+0Xextx1twLeoSGWBR6lflnKHoGRmP5EzkJ61BYoYPU0TvLYMi7DeGiL9w22DyZwj4D+8=",
        "HV0ihbn1GU3yvliLSfFV+H00asIwBnlN/FrXjo3bOS2bxGDCAL16HedvXmbTDrMGyAe6vuNvjCuj",
        "NwIG+p7+Cg/Kr269U/Yi+U92cMkCDVRF+kjKqsuCGDC/wmnBDYVfWLs2bHGUXg==",
        "HV0ihbn1GU3yvlirSfF20kcxbMIKHH5M60jH8IfUOQ==",
        "LRQYvPq3Hk3rq22/HvRm0QZGN/8LAHBq/EPCt4WCKjuugEHHDY1jS4owbHDVHpkC3h2zs/ZrxyWiNBKjXrQlyBaihRVr39THjZ4S1VTGBNVyRdEfwwSXfVQg/XM="
    ]

    key = "Osi2yzncUKrppHAEnF" # RC4 key

    for i, x in enumerate(encoded):
        result = decode_string(x, key)
        try:
            decoded = result.decode("utf-8")
        except UnicodeDecodeError:
            decoded = result.decode("latin1")
        print(f"| {x[:30]:<30} | {decoded} |")
