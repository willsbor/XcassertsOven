import copy
import getopt
import ntpath
import sys
import os
import io
import json
import shutil
from PIL import Image
from collections import OrderedDict

class XcassetsOvenErrorException(Exception):
    pass

class XcassetsOvenNotSupportTypeException(Exception):
    pass

def find_image_file(a_dir, a_extension_name='.png'):
    result = []
    for name in os.listdir(a_dir):
        full_path = os.path.join(a_dir, name)
        #print name
        #print full_path
        if os.path.isdir(full_path):
            result.extend(find_image_file(full_path,a_extension_name))
        elif name.endswith(a_extension_name):
            #print 'find ' + name
            result.append(full_path)
    return result

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def path_head(path):
    head, tail = ntpath.split(path)
    return ntpath.basename(head)

def filename_without_ext_type(a_filename):
    filenames = a_filename.split('.')
    return ".".join(filenames[:-1])

def filename_without_scale_number(a_filename):
    filenames = a_filename.split('@')
    if len(filenames) == 1:
        return a_filename
    else:
        return "@".join(filenames[:-1])

def init_content(a_type):
    author = 'xcode'
    if a_type == 'imageset':
        return {
            'images': [{'idiom': 'universal', 'scale': '1x'}, {'idiom': 'universal', 'scale': '2x'}, {'idiom': 'universal', 'scale': '3x'}],
            'info': {
                'version': 1,
                'author': author,
            },
        }
    elif a_type == 'appiconset':
        return {
            'images': [{
      "size" : "29x29",
      "idiom" : "iphone",
      "scale" : "2x"
    },
    {
      "size" : "29x29",
      "idiom" : "iphone",
      "scale" : "3x"
    },
    {
      "size" : "40x40",
      "idiom" : "iphone",
      "scale" : "2x"
    },
    {
      "size" : "40x40",
      "idiom" : "iphone",
      "scale" : "3x"
    },
    {
      "size" : "60x60",
      "idiom" : "iphone",
      "scale" : "2x"
    },
    {
      "size" : "60x60",
      "idiom" : "iphone",
      "scale" : "3x"
    },
    {
      "size" : "29x29",
      "idiom" : "ipad",
      "scale" : "1x"
    },
    {
      "size" : "29x29",
      "idiom" : "ipad",
      "scale" : "2x"
    },
    {
      "size" : "40x40",
      "idiom" : "ipad",
      "scale" : "1x"
    },
    {
      "size" : "40x40",
      "idiom" : "ipad",
      "scale" : "2x"
    },
    {
      "size" : "76x76",
      "idiom" : "ipad",
      "scale" : "1x"
    },
    {
      "size" : "76x76",
      "idiom" : "ipad",
      "scale" : "2x"
    },
    {
      "idiom" : "ipad",
      "size" : "83.5x83.5",
      "scale" : "2x"
    },
    {
      "idiom" : "mac",
      "size" : "16x16",
      "scale" : "1x"
    },
    {
      "idiom" : "mac",
      "size" : "16x16",
      "scale" : "2x"
    },
    {
      "idiom" : "mac",
      "size" : "32x32",
      "scale" : "1x"
    },
    {
      "idiom" : "mac",
      "size" : "32x32",
      "scale" : "2x"
    },
    {
      "idiom" : "mac",
      "size" : "128x128",
      "scale" : "1x"
    },
    {
      "idiom" : "mac",
      "size" : "128x128",
      "scale" : "2x"
    },
    {
      "idiom" : "mac",
      "size" : "256x256",
      "scale" : "1x"
    },
    {
      "idiom" : "mac",
      "size" : "256x256",
      "scale" : "2x"
    },
    {
      "size" : "512x512",
      "idiom" : "mac",
      "scale" : "1x"
    },
    {
      "size" : "512x512",
      "idiom" : "mac",
      "scale" : "2x"
    }],
            'info': {
                'version': 1,
                'author': author,
            },
            'properties' : {
                'pre-rendered' : True
            }
        }
    elif a_type == 'launchimage':
        return {
            'images': [{
      "extent" : "full-screen",
      "idiom" : "iphone",
      "subtype" : "736h",
      "minimum-system-version" : "8.0",
      "orientation" : "portrait",
      "scale" : "3x"
    },
    {
      "extent" : "full-screen",
      "idiom" : "iphone",
      "subtype" : "667h",
      "minimum-system-version" : "8.0",
      "orientation" : "portrait",
      "scale" : "2x"
    },
    {
      "orientation" : "portrait",
      "idiom" : "iphone",
      "extent" : "full-screen",
      "minimum-system-version" : "7.0",
      "scale" : "2x"
    },
    {
      "extent" : "full-screen",
      "idiom" : "iphone",
      "subtype" : "retina4",
      "minimum-system-version" : "7.0",
      "orientation" : "portrait",
      "scale" : "2x"
    }],
            'info': {
                'version': 1,
                'author': author,
            },
        }
    elif a_type == 'xcassets':
        return {
            'info': {
                'version': 1,
                'author': author,
            },
        }
    else:
        raise XcassetsOvenNotSupportTypeException({"message": "Not support this type", "type": a_type})

def _info_by_size(filename, idiom, size, scale):
    return {'filename': filename, 'idiom': idiom, 'size': "" + str(size / scale) + "x" + str(size / scale), 'scale': "" + str(scale) + "x"}

def _sort_json_key(items):
    #print "items = " + str(items)
    sort_order = ['size', 'extent', 'idiom', 'subtype', 'filename', 'scale', 'minimum-system-version', 'orientation', 'resizing']
    items_ordered = OrderedDict(sorted(items.iteritems(), key=lambda (k, v): sort_order.index(k)))
    #items_ordered = sorted(items.items(), key=lambda kv: kv[0])
    #print "items_ordered = " + str(items_ordered)
    return items_ordered

def _sort_json_key_in_list(a_list):
    #print "blist = " + str(a_list)
    list_order = []
    for info in a_list:
        list_order.append(_sort_json_key(info))
    #print "alist = " + str(list_order)
    return list_order

def init_infos_content(a_type, a_filename, a_path):
    infos = []
    
    if a_type == 'imageset':
        infos.append({'filename': a_filename, 'idiom': 'universal', 'scale': guess_scale_by_filename(a_filename)})
    elif a_type == 'appiconset':
        im = Image.open(a_path)
        xsize, ysize = im.size
        if xsize != ysize:
            raise XcassetsOvenErrorException({"message": "size incorrect", "size": im.size})

        if xsize == 29:
            infos.append(_info_by_size(a_filename, 'ipad', xsize, 1))
        elif xsize == 58:
            infos.append(_info_by_size(a_filename, 'ipad', xsize, 2))
            infos.append(_info_by_size(a_filename, 'iphone', xsize, 2))
        elif xsize == 87:
            infos.append(_info_by_size(a_filename, 'iphone', xsize, 3))
        elif xsize == 40:
            infos.append(_info_by_size(a_filename, 'ipad', xsize, 1))
        elif xsize == 80:
            infos.append(_info_by_size(a_filename, 'ipad', xsize, 2))
            infos.append(_info_by_size(a_filename, 'iphone', xsize, 2))
        elif xsize == 120:
            infos.append(_info_by_size(a_filename, 'iphone', xsize, 3))
            infos.append(_info_by_size(a_filename, 'iphone', xsize, 2))
        elif xsize == 180:
            infos.append(_info_by_size(a_filename, 'iphone', xsize, 3))
        elif xsize == 76:
            infos.append(_info_by_size(a_filename, 'ipad', xsize, 1))
        elif xsize == 152:
            infos.append(_info_by_size(a_filename, 'ipad', xsize, 2))
        elif xsize == 167:   # ipad pro
            infos.append(_info_by_size(a_filename, 'ipad', xsize, 2))
        else:
            raise XcassetsOvenErrorException({"message": "size unsupport", "size": im.size})
    elif a_type == 'launchimage':
        im = Image.open(a_path)
        xsize, ysize = im.size

        if xsize == 1242 and ysize == 2208:
            infos.append({'filename': a_filename, 'extent': 'full-screen', 'idiom': 'iphone', 'subtype': '736h', 'scale': '3x', 'orientation': 'portrait', 'minimum-system-version' : '8.0'})
        elif xsize == 750 and ysize == 1334:
            infos.append({'filename': a_filename, 'extent': 'full-screen', 'idiom': 'iphone', 'subtype': '667h', 'scale': '2x', 'orientation': 'portrait', 'minimum-system-version' : '8.0'})
        elif xsize == 640 and ysize == 1136:
            infos.append({'filename': a_filename, 'extent': 'full-screen', 'idiom': 'iphone', 'subtype': 'retina4', 'scale': '2x', 'orientation': 'portrait', 'minimum-system-version' : '7.0'})
        elif xsize == 640 and ysize == 960:
            infos.append({'filename': a_filename, 'extent': 'full-screen', 'idiom': 'iphone', 'scale': '2x', 'orientation': 'portrait', 'minimum-system-version' : '7.0'})
        else:
            raise XcassetsOvenErrorException({"message": "size unsupport", "size": im.size})
    else:
        raise XcassetsOvenNotSupportTypeException({"message": "Not support this type", "type": a_type})
    return infos

def guess_scale_by_filename(a_filename, a_filepath = ''):
    if a_filename.find('@2x') != -1:
        return '2x'
    elif a_filename.find('@3x') != -1:
        return '3x'
    else:
        return '1x'

def modify_info(a_info, a_given_info):
    a_info["scale"] = a_given_info["scale"]

def append_infos_into_content(a_sub_images, a_main_images, a_type):
    # add into [] by 
    # - imageset: scale + idiom or 
    # - appiconset:  size + scale + idiom 
    # - launchimage: subtype scale orientation

    for info in a_sub_images:
        ishit = False
        for m_info in a_main_images:
            if 'launchimage' == a_type:
                if info['scale'] == m_info['scale'] and info['orientation'] == m_info['orientation']:
                    if 'subtype' in info and 'subtype' in m_info and info['subtype'] == m_info['subtype']:
                        ishit = True
                        break
            elif 'imageset' == a_type:
                if info['idiom'] == m_info['idiom'] and info['scale'] == m_info['scale']:
                    ishit = True
                    break
            elif 'appiconset' == a_type:
                if info['idiom'] == m_info['idiom'] and info['scale'] == m_info['scale'] and info['size'] == m_info['size']:
                    ishit = True
                    break

        if ishit:
            #raise XcassetsOvenErrorException({"message": "duplicate setting for contents.json", "info": json.dumps(info), "main_images": json.dumps( a_main_images)})
            for key in iter(info):
                m_info[key] = info[key]
        else:
            a_main_images.append(info)

def create_xcassets_by_images(a_input_dir, a_result_dir, a_info_map, a_contents_map, a_set_parameter_map):
    if os.path.exists(a_result_dir):
        shutil.rmtree(a_result_dir)

    all_image_files = find_image_file(a_input_dir)

    # create sub xcassets dir
    for path in all_image_files:
        # get parent dir
        relative_path = path.replace(a_input_dir + "/", "")
        category_path = path_head(path)
        filename = path_leaf(path)

        if filename in a_info_map:
            if a_info_map[filename]['state'] == 'once':
                raise XcassetsOvenErrorException({"message": "filename is duplicated", "filename": filename, "category_path": category_path})

            print "get from infos.txt [" + relative_path + "]"
            a_info_map[filename]['state'] = 'once'
            set_name = a_info_map[filename]["set"]
            set_type = a_info_map[filename]["type"]
        else:
            print "parse by filename [" + relative_path + "]"
            set_name = filename_without_ext_type(filename)
            set_name = filename_without_scale_number(set_name)
            set_type = "imageset"
            a_info_map[filename] = {}
            a_info_map[filename]['state'] = 'once'
            a_info_map[filename]['type'] = set_type
            a_info_map[filename]['set'] = set_name
            a_info_map[filename]['images'] = init_infos_content(set_type, filename, path)

        set_content_file = a_result_dir + "/" + category_path + ".xcassets" + "/" + "Contents.json"
        if set_content_file not in a_contents_map:
           a_contents_map[set_content_file] = init_content('xcassets')

        # Contents.json
        content_file = a_result_dir + "/" + category_path + ".xcassets" + "/" + set_name + "." + set_type + "/Contents.json"
        if content_file not in a_contents_map:
            a_contents_map[content_file] = init_content(set_type)
            p_key = set_name + "." + set_type
            if p_key in a_set_parameter_map:
                for pp_key in iter(a_set_parameter_map[p_key]):
                    a_contents_map[content_file][pp_key] = a_set_parameter_map[p_key][pp_key]
        content = a_contents_map[content_file]

        # add image info into Contents.json
        append_infos_into_content(a_info_map[filename]['images'], content['images'], set_type)

        # TODO: add more type or resize image if it lose

        dst = a_result_dir + "/" + category_path + ".xcassets" + "/" + set_name + "." + set_type + "/" + filename
        directory = os.path.dirname(dst)
        if not os.path.exists(directory):
            os.makedirs(directory)
        shutil.copyfile(path, dst)

def get_contents_map(a_input_dir):
    all_content_files = find_image_file(a_input_dir, '.json')

    content_map = {}
    # create sub xcassets dir
    for path in all_content_files:
        relative_path = path.replace(a_input_dir + "/", "")

        head, filename = ntpath.split(relative_path)
        category, set_name_type = ntpath.split(head)
        set_name, set_type = set_name_type.split('.', 2)
        category = category.split('.')[0]

        info = json_dict_for_file_path(path)
        content_map[set_name] = info

    return content_map

def get_specific_filename(a_content_map, a_filename):
    result = []
    for info in a_content_map['images']:
        if 'filename' in info and info['filename'] == a_filename:
            result.append(info)
    return result

def parse_xcassets(a_input_dir, a_result_dir, info_file):
    if a_result_dir is not None and os.path.exists(a_result_dir):
        shutil.rmtree(a_result_dir)

    content_map = get_contents_map(a_input_dir)
    all_image_files = find_image_file(a_input_dir)

    info_map = {}
    set_parameter = {}
    # create sub xcassets dir
    for path in all_image_files:
        # get parent dir
        relative_path = path.replace(a_input_dir + "/", "")

        head, filename = ntpath.split(relative_path)
        category, set_name_type = ntpath.split(head)
        set_name, set_type = set_name_type.split('.', 2)
        category = category.split('.')[0]

        if filename in info_map:
            raise XcassetsOvenErrorException({"message": "duplicate filename", "filename": filename, "relative_path": relative_path})

        info = {}
        info['state'] = 'ok'
        info['set'] = set_name
        info['type'] = set_type
        info['images'] = get_specific_filename(content_map[set_name], filename)
        info_map[filename] = info

        # remember other setting for a set
        set_parameter[set_name + "." + set_type] = content_map[set_name]

        if a_result_dir is not None:
            dst = a_result_dir + "/" + category + "/" + filename
            directory = os.path.dirname(dst)
            if not os.path.exists(directory):
                os.makedirs(directory)
            shutil.copyfile(path, dst)

    write_info_map(info_file, info_map, set_parameter)

def ascii_encode_dict(data):
    ascii_encode = lambda x: x.encode('ascii')
    return dict(map(ascii_encode, pair) for pair in data.items())

def read_info_map(a_filepath):
    if not os.path.exists(a_filepath):
        return {}

    infos_map = {}
    set_parameter_map = {}
    with open(a_filepath) as f:
        content = f.readlines()
        for line in content:
            line = line[:-1]  # remove \n
            infos = line.split(", ", 4)
            if len(infos) == 5:
                if infos[0] == "set-p":
                    set_parameter_map[infos[1]] = json.loads(infos[4])
                else:
                    infos_map[infos[1]] = {}
                    infos_map[infos[1]]["state"] = infos[0]
                    infos_map[infos[1]]["set"] = infos[2]
                    infos_map[infos[1]]["type"] = infos[3]
                    infos_map[infos[1]]["images"] = json.loads(infos[4]) #, object_hook=ascii_encode_dict
            else:
                print "false : [" + str(len(infos)) + "]" + line
    return (infos_map, set_parameter_map)

def write_info_map(a_filepath, a_info_map, a_set_parameters):
    directory = os.path.dirname(a_filepath)
    if directory != '' and not os.path.exists(directory):
        os.makedirs(directory)

    sorted_info_map = OrderedDict(sorted(a_info_map.items()))

    f = io.open(a_filepath, 'wb')
    for info_key in iter(sorted_info_map):
        info = a_info_map[info_key]
        f.write("" + "ok" + ", "
          + info_key + ", "
          + info['set'] + ", "
          + info['type'] + ", "
          + json.dumps(_sort_json_key_in_list(info['images'])) + "\n")

    sorted_set_parameters = OrderedDict(sorted(a_set_parameters.items()))
    for key in iter(sorted_set_parameters):
        content_json = a_set_parameters[key]
        without_image = copy.copy(content_json)
        if 'images' in without_image:
            without_image.pop('images', None)
        f.write("" + "set-p" + ", "
          + key + ", "
          + ", "
          + ", "
          + json.dumps(without_image) + "\n")
    
    f.close()

def json_dict_for_file_path(file_path):
    if os.path.exists(file_path):
        return json.load(open(file_path, 'r')) # , object_hook=ascii_encode_dict
    return None

def write_dict_to_file_path(file_path, info):
    json_file = open(file_path, 'w+')
    json_file.write(json.dumps(info, indent=2, separators=(',',' : ')))
    json_file.close()

def create_contents_files(a_contents_map):
    print "create_contents_files..."
    for path in iter(a_contents_map):
        content = a_contents_map[path]
        if 'images' in content:
            content['images'] = _sort_json_key_in_list(content['images'])
        write_dict_to_file_path(path, content)

def main(argv):

    images_dir = None
    result_dir = None
    info_file = "xcassets_info.txt"
    command = None

    try:
        opts, args = getopt.getopt(argv,
            "ho:c:p:i:",
            ["output=","create-xcassets=","parse-xcassets=","info-file="])
    except getopt.GetoptError:
        print 'error: parse.py wrong command'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
           print 'parse.py ????'
           sys.exit()
        elif opt in ("-c", "--create-xcassets"):
            command = "c"
            images_dir = arg
        elif opt in ("-p", "--parse-xcassets"):
            command = "p"
            images_dir = arg
        elif opt in ("-o", "--output"):
            result_dir = arg
        elif opt in ("-i", "--info-file"):
            info_file = arg

    if images_dir is not None:
        images_dir = os.path.abspath(os.path.normpath(images_dir))
    if result_dir is not None:
        result_dir = os.path.abspath(os.path.normpath(result_dir))
    if info_file is not None:
        info_file = os.path.abspath(os.path.normpath(info_file))

    print "source_dir = " + str(images_dir)
    print "output = " + str(result_dir)
    print "info file = " + str(info_file)

    if command == "c":
        info_map, set_parameter_map = read_info_map(info_file)
        contents_map = {}
        create_xcassets_by_images(images_dir, result_dir, info_map, contents_map, set_parameter_map)
        create_contents_files(contents_map)
        write_info_map(info_file, info_map, set_parameter_map)
    elif command == "p":
        parse_xcassets(images_dir, result_dir, info_file)
    else:
        print 'parse.py ????'
        sys.exit()
   
if __name__ == "__main__":
   main(sys.argv[1:])