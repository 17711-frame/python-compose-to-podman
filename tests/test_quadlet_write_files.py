# Part of the project compose-to-quadlet — Licensed under MIT © The 17711 Frame (https://17711.org)
from compose_to_quadlet.compose_parser import parse_compose_yaml
from compose_to_quadlet.quadlet_writer import write_quadlets
from unittest.mock import patch, mock_open, call, MagicMock
import os

def test_quadlet_write_files(tmp_path):
    yml = '''
services:
  web:
    image: nginx
    ports:
      - "8080:80"
    volumes:
      - ./html:/usr/share/nginx/html:ro
    environment:
      - NGINX_HOST=localhost
  db:
    image: postgres
    environment:
      DB_NAME: mydb
volumes:
  data:
networks:
  front:
'''
    spec = parse_compose_yaml(yml)
    output_dir = tmp_path / "quadlets"

    written_content = {}

    def mock_open_side_effect(path, *args, **kwargs):
        handle = MagicMock()
        handle.__enter__.return_value = handle
        handle.write.side_effect = lambda data: written_content.setdefault(path, []).append(data)
        return handle

    with patch("builtins.open", side_effect=mock_open_side_effect) as mock_opener:
        files = write_quadlets(spec, output_dir.as_posix())

        assert len(files) == 4
        
        web_path = os.path.join(output_dir, "web.container")
        db_path = os.path.join(output_dir, "db.container")
        data_path = os.path.join(output_dir, "data.volume")
        front_path = os.path.join(output_dir, "front.network")

        web_content = "".join(written_content.get(web_path, []))
        db_content = "".join(written_content.get(db_path, []))
        data_content = "".join(written_content.get(data_path, []))
        front_content = "".join(written_content.get(front_path, []))

        assert "Image=nginx" in web_content
        assert "PublishPort=8080:80" in web_content
        assert "Volume=./html:/usr/share/nginx/html:ro" in web_content
        assert "Environment=NGINX_HOST=localhost" in web_content
        assert "Image=postgres" in db_content
        assert "Environment=DB_NAME=mydb" in db_content
        assert "VolumeName=data" in data_content
        assert "Name=front" in front_content


def test_quadlet_write_skips_external_resources(tmp_path):
    yml = '''
volumes:
  ext_vol:
    external: true
networks:
  ext_net:
    external: true
'''
    spec = parse_compose_yaml(yml)
    output_dir = tmp_path / "quadlets"
    
    with patch("builtins.open", mock_open()) as mock_file:
        files = write_quadlets(spec, output_dir.as_posix())
        assert len(files) == 0
        mock_file.assert_not_called()
