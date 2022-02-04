
import fitz
import os


def get_html(file_path, file_name):

    # Creates HTML output of pdf
    html_path = os.path.join(file_path, f'{file_name}.html')
    doc = fitz.open(os.path.join(file_path, f'{file_name}.pdf'))
    html_file = open(html_path, 'a')
    for page in doc.pages():
        html_data = page.get_text('html')
        html_file.write(html_data)


def get_json(file_path, file_name):

    # creates full JSON image of pdf
    path = os.path.join(file_path, f'{file_name}_JSON.txt')
    doc = fitz.open(os.path.join(file_path, f'{file_name}.pdf'))
    html_file = open(path, 'a')
    for page in doc.pages():
        html_data = page.get_text('json')
        html_file.write(html_data)


def get_dict(file_path, file_name):

    # for now we are only extract text
    '''returns dictionary in below format
    pdf_dict_list = [{
        'page_no' : int_page_no
        'spans' : text details
    } ]
    '''
    doc = fitz.open(os.path.join(file_path, f'{file_name}.pdf'))
    print(f" No of pages {len(doc)}")
    page_List_dir = []
    page_no = 1
    print('file path is {}'.format(file_path),
          '\nfile Name  is  {}'.format(file_name))

    for page in doc.pages():
        page_dir = {}
        page_dir['page_no'] = page_no
        page_dir['spans'] = []
        dict_page = page.get_text('dict')
        page_blocks = dict_page['blocks']
        for b in page_blocks:
            if b['type'] == 0:
                # Captures all text blocks
                for line in b['lines']:
                    # lines in each block
                    for span in line['spans']:
                        page_dir['spans'].append(span)

            if b['type'] == 1:
                # Captures all image Blocks
                # type '1' is image blocks can be extracted as required
                pass
        page_List_dir.append(page_dir)
        page_no += 1

    return page_List_dir


def tuner():
    # takes pdf as input and finds the possible values of Header and Footer spaces
    # We can tune the output performing the checking
    # human leval tuning can be done in initial vertions
    # Automated tuning should be done is the next target
    pass


def header_remover(page_dict):
    # takes output of get_dict
    """
       # Upper Limit  y = 105
       # Lower Limit y = 750
    """
    fpage_dict = []

    for page in page_dict:
        d = {
            'page_no': page['page_no'],
            'spans': []
        }

        for span in page['spans']:
            y = span['bbox'][1]
            if (y >= 105) and (y <= 750):
                d['spans'].append(span)

        fpage_dict.append(d)

    return fpage_dict


def find_table():
    '''returns positons of table in pdf
    dir = {
        page_n0 : '',
        position : '',
    }
    '''
    pass


template_format = {

    # template models can be added as per requirement
    1: {
        'Headings': ['INDEX', 'SCOPE', 'OBJECT', 'REVIEW', 'RELATED DOCUMENTS', 'REQUIREMENTS', 'CHANGE HISTORY'],
        'discription': "All Headings are Bold and in Capital Casing "

    },
    2: {
        'Headings': [],
        'discription': ""
    }
}

#---------------------Inputs-------------------------------#

file_path = r'C:\Users\rprathik\Desktop\data_files'
file_name = 'STJLR-06-5042'

# print(get_dict(file_path, file_name))
file = open(r'C:\Users\rprathik\Desktop\data_files\test_page.txt', 'a')
page_dict = get_dict(file_path, file_name)
# print(page_dict[0])

# Geting Headers, Shall be refactored in to Function
heading_details = [
    # list of dicts
]
header_id = 0
for d in page_dict:
    for span in d['spans']:

        if span['font'] == 'Arial-BoldMT':
            # get all bold letter
            if span['text'].isupper():
                # get all Upper case headers
                details = {
                    'page_no': d['page_no'],
                    'text': span['text'],
                    'bbox': span['bbox']
                }

                heading_details.append(details)


# Filter Headings as per template model
headings = []

for s in heading_details:
    if (s['text'].strip() in template_format[1]['Headings']):
        # print(s['text'], "---- is filterd", f" in Page  {s['page_no']} ")
        # 'heading' has list of headings text,page_no and bbox
        headings.append(s)


# header_remover(page_dict)
fpage_dict = header_remover(page_dict)


# get text between the headings

pdf_data = []


'''upper_limit = headings[1]['bbox'][1]
lower_limit = headings[2]['bbox'][1]

page = fpage_dict[0]

for span in page['spans']:

    span_y = span['bbox'][1]
    if (upper_limit < span_y) and (lower_limit > span_y):
        print(span['text'])'''

# print(headings)

# get limits of Each headings

headings_limits = []

'''target dir
    {
        heading : ''
        page_range : 1,2,.6
    }

    '''

no_pages = len(fpage_dict)
for heading in headings:
    d = {}
    d['heading'] = heading['text']
    index = headings.index(heading)
    if heading != headings[-1]:
        t = (heading['page_no'], headings[index+1]['page_no'] + 1)
        d['limits'] = list(range(t[0], t[1]))
        d['y_limits'] = [heading['bbox'][1], headings[index+1]['bbox'][1]]
    else:
        t = (heading['page_no'], no_pages+1)
        d['limits'] = list(range(t[0], t[1]))
        d['y_limits'] = [heading['bbox'][1]]
    headings_limits.append(d)

# adding y limits to heading_limits
'''target dir
        headings_limits[]
    {
        heading : ''
        page_range : [3,4,5]
        'y_limits' : (y1,y2)
    }

    '''


# heding data has heading wise sorted text and
heading_data = []

'''{
    heading : ''
    spans : []
}
'''

# looping on heading_limits and append on

for h in headings_limits:
    index = headings_limits.index(h)
    d = {
        'heading': h['heading'],
        'spans': []
    }
    if len(h['limits']) == 1:
        upper_limit = h['y_limits'][0]
        lower_limit = h['y_limits'][1]

        for page in fpage_dict:
            if page["page_no"] == h['limits'][0]:
                for span in page['spans']:
                    span_y = span['bbox'][1]
                    if (upper_limit < span_y) and (lower_limit > span_y):
                        # print(span['text'])
                        d['spans'].append(span)

    elif len(h['limits']) == 2 and h != headings_limits[-1]:
        for page in fpage_dict:
            if page["page_no"] == h['limits'][0]:
                # print('------'*10, page["page_no"])
                upper_limit_page_1 = h['y_limits'][0]
                for span in page['spans']:
                    span_y = span['bbox'][1]
                    if (upper_limit_page_1 < span_y):
                        d['spans'].append(span)
                        # print(span['text'])

            if page["page_no"] == h['limits'][-1]:
                # print('------'*10, page["page_no"])
                lower_limit_page_1 = h['y_limits'][1]
                for span in page['spans']:
                    span_y = span['bbox'][1]
                    if (lower_limit_page_1 > span_y):
                        d['spans'].append(span)
                        # print(span['text'])

    elif len(h['limits']) > 2 and h != headings_limits[-1]:
        for page in fpage_dict:
            if page['page_no'] == h['limits'][0]:

                upper_limit_page_1 = h['y_limits'][0]
                for span in page['spans']:
                    span_y = span['bbox'][1]
                    if (upper_limit_page_1 < span_y):
                        d['spans'].append(span)

            elif (page['page_no'] in h['limits'][1: -1]):

                for span in page['spans']:
                    d['spans'].append(span)

            elif page['page_no'] == h['limits'][-1]:

                lowerlimit_last_page = h['y_limits'][1]
                for span in page['spans']:
                    span_y = span['bbox'][1]
                    if (lowerlimit_last_page > span_y):
                        d['spans'].append(span)

    elif h == headings_limits[-1]:
        for page in fpage_dict:
            if page['page_no'] == h['limits'][0]:

                upper_limit_page_1 = h['y_limits'][0]
                for span in page['spans']:
                    span_y = span['bbox'][1]
                    if (upper_limit_page_1 < span_y):

                        d['spans'].append(span)
            if (page['page_no'] in h['limits'][1:]):
                for span in page['spans']:
                    print(span['text'])
                    d['spans'].append(span)

    heading_data.append(d)


for i in headings_limits:
    print(i)

for i in heading_data:
    print(i['heading'])
    f = open(f"{i['heading']}_file.txt","a+",encoding="utf-8")
    for span in i['spans'] :
        text = span['text']
        html = "<p>" + text.replace("\n", "<br>") + "</p>"
        f.write("<br>")
        f.write(html)    
    f.close()
    
    

s

