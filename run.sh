# 容器名称
NAME="discord-bot"

# 停止并删除旧的容器
if [ "$(docker ps -q -f name=$NAME)" ]; then
    echo "Stopping and removing existing container: $NAME"
    docker kill $NAME
    docker rm $NAME
else
    echo "No running container found with the name: $NAME"
fi

# 构建新的 Docker 镜像
echo "Building new Docker image: $NAME"
docker build -t $NAME .

# 运行新的 Docker 容器
echo "Running new Docker container: $NAME"
docker run -d --name $NAME $NAME

# 检查容器日志
echo "Tailing logs for container: $NAME"
docker logs -f $NAME