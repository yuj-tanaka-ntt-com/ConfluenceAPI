from typing import Dict, List

# ページデータからコンテンツを抽出

def extract_page_content(page_data: Dict) -> Dict:
    return {
        'id': page_data.get('id'),
        'title': page_data.get('title'),
        'type': page_data.get('type'),
        'status': page_data.get('status'),
        'space_key': page_data.get('space', {}).get('key'),
        'space_name': page_data.get('space', {}).get('name'),
        'content': page_data.get('body', {}).get('storage', {}).get('value', ''),
        'version': page_data.get('version', {}).get('number'),
        'created': page_data.get('created'),
        'updated': page_data.get('version', {}).get('when'),
        'url': page_data.get('_links', {}).get('webui', '')
    }

# ページリストから階層構造（ツリー）を構築

def build_page_tree(pages: List[Dict]) -> List[Dict]:
    page_dict = {page['id']: page for page in pages}
    tree = []
    for page in pages:
        parent_id = page.get('parentId')
        if parent_id and parent_id in page_dict:
            parent = page_dict[parent_id]
            if 'children' not in parent:
                parent['children'] = []
            parent['children'].append(page)
        else:
            tree.append(page)
    return tree

# descendantsリストから階層ツリーを構築

def build_descendants_tree(descendants: List[Dict], ancestor_id: str) -> Dict:
    id_to_node = {item['id']: item for item in descendants}
    tree = []
    flat_list = []
    for item in descendants:
        ancestors = item.get('ancestors', [])
        if ancestors and ancestors[-1].get('id') == ancestor_id:
            tree.append(item)
        flat_list.append(item)
    return {'tree': tree, 'flat_list': flat_list, 'total_count': len(flat_list)} 