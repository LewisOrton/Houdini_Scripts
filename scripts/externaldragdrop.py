# drag and drop to import file in Houdini
# by Lewis Orton
# https://vimeo.com/lewisorton

import hou, re, os, sys

def dropAccept(files):

    pane = hou.ui.paneTabUnderCursor() 
    if (pane.type().name() != "NetworkEditor"):
        return False

    for file in files:
        #windows file path contains special prefix which needs to be removed
        if file[0:8] == "file:///":
            file_path = file[8:]
        else:
            file_path = file
        
        file_basename = os.path.splitext(os.path.basename(file_path))
        file_ext = file_basename[1].lower()

        #convert to relative path
        file_path = rel_path(file_path)
        
        cursor_position = pane.cursorPosition()
        network_node = pane.pwd()

        if re.match(".hip", file_ext) != None:
            hou.hipFile.load(file_path)
            return True
        try:
            import_file(network_node, file_path, file_basename, cursor_position)
            return True
        except:
            print(sys.exc_info()[1])
            return False

    return False

def rel_path(fullpath):
    hippath = hou.getenv("HIP")
    if re.match(hippath, fullpath):
        fullpath = "$HIP" +  re.sub(hippath, "", fullpath)
    return fullpath

def import_file(network_node, file_path, file_basename, cursor_position):
    #validate node name
    file_name = re.sub(r"[^0-9a-zA-Z\.]+", "_", file_basename[0])
    file_ext = file_basename[1].lower()
    
    #create new geo node in obj network if none exists
    if network_node.type().name() == "obj":
        network_node = network_node.createNode("geo", "GEO_" + file_name)
        network_node.setPosition(cursor_position)

    if network_node.type().name() == "geo":
        if file_ext == ".abc":
            create_new_node(network_node, file_path, "alembic", "fileName", cursor_position)
            return True
        elif file_ext == ".rs":
            create_new_node(network_node, file_path, "redshift_packedProxySOP", "RS_proxy_file", cursor_position)
            return True
        elif file_ext == ".ass":
            create_new_node(network_node, file_path, "arnold_asstoc", "ass_file", cursor_position)
            return True
        else:
            create_new_node(network_node, file_path, "file", "file", cursor_position)
            return True
    elif network_node.type().name() in {"mat","materialbuilder", "materiallibrary"}:
        create_new_node(network_node, file_path, "texture::2.0", "map", cursor_position)
        return True
    elif network_node.type().name() == "redshift_vopnet":
        create_new_node(network_node, file_path, "redshift::TextureSampler", "tex0", cursor_position)
        return True
    elif network_node.type().name() == "chopnet":
        create_new_node(network_node, file_path, "file", "file", cursor_position)
        return True
    elif network_node.type().name() in {"arnold_materialbuilder", "arnold_vopnet"}:
        create_new_node(network_node, file_path, "arnold::image", "filename", cursor_position)
        return True
    elif network_node.type().name() in {"cop2net", "img"}:
        create_new_node(network_node, file_path, "file", "filename1", cursor_position)
        return True
    return False

def create_new_node(network_node, file_path, node_name, parm_path_name, cursor_position):
    new_node = network_node.createNode(node_name)
    new_node.setPosition(cursor_position)
    new_node.setParms({parm_path_name:file_path})
    return new_node
