# pdfPRINT

## Deployment

- Install `gunicorn`
    ```
    apt install gunicorn
    ```

- run `gunicorn`
    ```
    gunicorn --bind 0.0.0.0:8000 pdf_print.wsgi
    ```
- Install `nginx`
    ```
    apt install nginx
    ```
- Open the nginx configuration `/etc/nginx/sites-enabled/default` and add the following lines.
    ```
    server {
            listen 80;


            location / {
                proxy_pass http://localhost:8000;
            }
            location /static {
                autoindex on;
                alias /data/static;
            }
        }
    ```
- Do not forget to set the maximum file upload size in nginx in the `/etc/nginx/nginx.conf` file
    ```
    client_max_body_size 200M;
    ```
