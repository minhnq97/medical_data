#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020 minhnq <minhnq@rd04>
#
# Distributed under terms of the MIT license.


from preprocess import _format_line, load_data, merge_data_by_category, drop_category, redefine_data
from elasticsearch.helpers import bulk
from elasticsearch  import Elasticsearch

def gen_bulk(all_data, index_name="index_name"):
    cate_dict={}
    with open("mapping_category.txt", "rt") as f:
        for line in f.read().splitlines():
            id, cate = line.split(None,1)
            cate_dict[id] = cate
    for data, label in all_data:
        yield {
            "_index": index_name,
            "question": data,
            "preprocessed_question":_format_line(data),
            "category_id": label,
            "category":cate_dict[label],
            "keywords": [],
        }

def create_bulk():
    all_data = load_data("crawl_md_question/")
    all_data, label_list = merge_data_by_category(all_data, target_merge={'c22':'c22', 'c57':'c22', 'c55':'c22',
                                                                         'c11':'c22','c33':'c22','c10':'c22','c34':'c22', # c22: nội khoa
                                                                         'c5':'c5','c3':'c5','c21':'c21','c19':'c21','c4':'c21'}) #c5: viêm gan; c21: sản phụ khoa
    all_data, label_list = drop_category(all_data, drop_target=['c20','c17','c73'])
    all_data, label_list = redefine_data(all_data, threshold=50)
    return all_data, label_list

if __name__ == '__main__':
    elastic_client = Elasticsearch(hosts=["localhost"])
    all_data, label_list = create_bulk()
    bulk(elastic_client,gen_bulk(all_data, index_name="new_medlatec"))
