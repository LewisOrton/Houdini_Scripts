# drag and drop to import file in Houdini
# by Lewis Orton
# https://vimeo.com/lewisorton

import hou, re, os, sys, platform

if sys.version_info.major < 3:
    from urllib import unquote
else:
    from urllib.parse import unquote
#decode urlpath on windows

def dropAccept(files):
    pane = hou.ui.paneTabUnderCursor() 
    if (pane.type().name() != "NetworkEditor"):
        return False
    hversion = hou.applicationVersion()
    
    for i, file in enumerate(files):
        if (hversion[0] < 18) or (hversion[0] == 18 and hversion[1] == 0):
            
            #print("hversion < 18.5")
            if platform.system() == "Windows":
                file_path = file[8:]
            elif platform.system() == "Linux":
                file_path = file[7:]
        else:
            file_path = file
            #print(file)


        file_path = unquote(file_path) #decode urlpath

        file_basename = os.path.splitext(os.path.basename(file_path))
        file_ext = file_basename[1].lower()

        #convert to relative path
        file_path = rel_path(file_path)
        
        cursor_position = pane.cursorPosition() + hou.Vector2(i *3, 0)

        network_node = pane.pwd()

        #opening hip
        if re.match(".hip", file_ext) != None:
            hou.hipFile.load(file_path)
            return True

        #adding nodes
        try:
            import_file(network_node, file_path, file_basename, file_ext, cursor_position)
        except:
            print(sys.exc_info()[1])
            return False

    return True

def rel_path(fullpath):
    hippath = hou.getenv("HIP")
    if re.match(hippath, fullpath):
        fullpath = "$HIP" +  re.sub(hippath, "", fullpath)
    return fullpath

def import_file(network_node, file_path, file_basename, file_ext, cursor_position):
    #validate node name
    file_name = re.sub(r"[^0-9a-zA-Z\.]+", "_", file_basename[0])
    #create new geo node in obj network if none exists

    net_type_name = network_node.type().name()

    if net_type_name == "obj":
        network_node = network_node.createNode("geo", "GEO_" + file_name)
        network_node.setPosition(cursor_position)

    #if target network is a subnet, get the real network type by looking up to parents
    if net_type_name == "subnet":
        parent = network_node.parent()
        while parent.type().name() == "subnet":
            parent = parent.parent()
        net_type_name = parent.type().name()
    
    #karma detection
    if net_type_name == "materiallibrary":
        test_nodes = network_node.children()
        for test_node in test_nodes:
            if test_node.type().name()[:4] == "mtlx" or "kma":
                net_type_name = "karma_subnet"
                break

    if net_type_name in {"geo","sopnet"}:
        if file_ext == ".abc":
            create_new_node(network_node, file_path, "alembic", "fileName", cursor_position, name = file_name)
            return True
        elif file_ext == ".rs":
            create_new_node(network_node, file_path, "redshift_packedProxySOP", "RS_proxy_file", cursor_position, name = file_name)
            return True
        elif file_ext == ".ass":
            create_new_node(network_node, file_path, "arnold_asstoc", "ass_file", cursor_position, name = file_name)
            return True
        elif file_ext in {".usd", ".usda", ".usdc"}:
            create_new_node(network_node, file_path, "usdimport", "filepath1", cursor_position, name = file_name)
        else:
            create_new_node(network_node, file_path, "file", "file", cursor_position, name = file_name)
            return True
    elif net_type_name in {"mat","materialbuilder", "materiallibrary"}:
        create_new_node(network_node, file_path, "texture::2.0", "map", cursor_position, name = file_name)
        return True
    elif net_type_name == "redshift_vopnet":
        create_new_node(network_node, file_path, "redshift::TextureSampler", "tex0", cursor_position, name = file_name)
        return True
    elif net_type_name == "chopnet":
        create_new_node(network_node, file_path, "file", "file", cursor_position, name = file_name)
        return True
    elif net_type_name in {"arnold_materialbuilder", "arnold_vopnet"}:
        create_new_node(network_node, file_path, "arnold::image", "filename", cursor_position, name = file_name)
        return True
    elif net_type_name in {"cop2net", "img"}:
        create_new_node(network_node, file_path, "file", "filename1", cursor_position, name = file_name)
        return True
    elif net_type_name in {"lopnet","stage"}:
        create_new_node(network_node, file_path, "reference", "filepath1", cursor_position, name = file_name)
        return True
    elif net_type_name == "karma_subnet":
        create_new_node(network_node, file_path, "mtlximage", "file", cursor_position, name = file_name)
        return True
    elif net_type_name == "octane_vopnet":
        octane_texture = create_new_node(network_node, file_path, "octane::NT_TEX_IMAGE", "A_FILENAME", cursor_position, name = file_name)
        octane_transform = network_node.createNode("octane::NT_TRANSFORM_2D")
        octane_transform.setPosition(cursor_position - hou.Vector2(2,0.8))
        octane_texture.setInput(5, octane_transform, 0)
        return True
    return False

def create_new_node(network_node, file_path, node_name, parm_path_name, cursor_position, **kwargs):
    name =  kwargs.get('name', None)
    if name:
        new_node = network_node.createNode(node_name, name)
    else:
        new_node = network_node.createNode(node_name)
    new_node.setPosition(cursor_position)
    new_node.setParms({parm_path_name:file_path})
    return new_node
