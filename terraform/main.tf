provider "aws" {
  region = "eu-west-2"
}

resource "aws_ecs_cluster" "c8-annie-trucks-terraform-cluster" {
  name = "c8-annie-trucks-terraform-cluster"
}

resource "aws_ecs_task_definition" "c8-annie-trucks-pipeline-terraform" {
  family = "c8-annie-trucks-pipeline-terraform"
  container_definitions = jsonencode([
    {
      "name" : "c8-annie-pipeline-ecr",
      "image" : "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c8-annie-pipeline-ecr",
      "cpu" : 0,
      "portMappings" : [
        {
          "name" : "c8-annie-truck-pipeline-port-mappings-tf",
          "containerPort" : 80,
          "hostPort" : 80,
          "protocol" : "tcp",
          "appProtocol" : "http"
        }
      ],
      "essential" : true,
      "environment" : [
        {
          "name" : "ACCESS_KEY_ID",
          "value" : "AKIAR4CX2OZCXZ5I3CZI"
        },
        {
          "name" : "SECRET_ACCESS_KEY",
          "value" : "26ChWggCbEhB1Cqkq5butkgbgJeiykgnG+NZ7uDF"
        },
        {
          "name" : "BUCKET_NAME",
          "value" : "sigma-resources-truck"
        },
        {
          "name" : "DB_HOST",
          "value" : "c8-redshift-cluster.cdq12ms5gjyk.eu-west-2.redshift.amazonaws.com"
        },
        {
          "name" : "DB_PORT",
          "value" : "5439"
        },
        {
          "name" : "DB_NAME",
          "value" : "dev"
        },
        {
          "name" : "DB_USER",
          "value" : "sigma_annie"
        },
        {
          "name" : "DB_PASSWORD",
          "value" : "Sigmapass1"
        },
        {
          "name" : "DB_SCHEMA",
          "value" : "sigma_annie_schema"
        }
      ],
      "environmentFiles" : [],
      "mountPoints" : [],
      "volumesFrom" : [],
      "ulimits" : [],
      "logConfiguration" : {
        "logDriver" : "awslogs",
        "options" : {
          "awslogs-create-group" : "true",
          "awslogs-group" : "/ecs/",
          "awslogs-region" : "eu-west-2",
          "awslogs-stream-prefix" : "ecs"
        },
        "secretOptions" : []
      }
    }
  ])
  execution_role_arn       = "arn:aws:iam::129033205317:role/ecsTaskExecutionRole"
  task_role_arn            = "arn:aws:iam::129033205317:role/ecsTaskExecutionRole"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"
  memory                   = "3072"

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }
}

resource "aws_ecs_task_definition" "c8-annie-dashboard-task-terraform" {
  family = "c8-annie-dashboard-task-terraform"
  container_definitions = jsonencode([
    {
      "name" : "c8-annie-dashboard-task-terraform",
      "image" : "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c8-annie-food-trucks-dashboard",
      "cpu" : 0,
      "portMappings" : [
        {
          "name" : "c8-annie-truck-pipeline-port-mappings-tf",
          "containerPort" : 80,
          "hostPort" : 80,
          "protocol" : "tcp",
          "appProtocol" : "http"
        }
      ],
      "essential" : true,
      "environment" : [
        {
          "name" : "ACCESS_KEY_ID",
          "value" : "AKIAR4CX2OZCXZ5I3CZI"
        },
        {
          "name" : "SECRET_ACCESS_KEY",
          "value" : "26ChWggCbEhB1Cqkq5butkgbgJeiykgnG+NZ7uDF"
        },
        {
          "name" : "BUCKET_NAME",
          "value" : "sigma-resources-truck"
        },
        {
          "name" : "DB_HOST",
          "value" : "c8-redshift-cluster.cdq12ms5gjyk.eu-west-2.redshift.amazonaws.com"
        },
        {
          "name" : "DB_PORT",
          "value" : "5439"
        },
        {
          "name" : "DB_NAME",
          "value" : "dev"
        },
        {
          "name" : "DB_USER",
          "value" : "sigma_annie"
        },
        {
          "name" : "DB_PASSWORD",
          "value" : "Sigmapass1"
        },
        {
          "name" : "DB_SCHEMA",
          "value" : "sigma_annie_schema"
        }
      ],
      "environmentFiles" : [],
      "mountPoints" : [],
      "volumesFrom" : [],
      "ulimits" : [],
      "logConfiguration" : {
        "logDriver" : "awslogs",
        "options" : {
          "awslogs-create-group" : "true",
          "awslogs-group" : "/ecs/",
          "awslogs-region" : "eu-west-2",
          "awslogs-stream-prefix" : "ecs"
        },
        "secretOptions" : []
      }
    }
  ])
  execution_role_arn       = "arn:aws:iam::129033205317:role/ecsTaskExecutionRole"
  task_role_arn            = "arn:aws:iam::129033205317:role/ecsTaskExecutionRole"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"
  memory                   = "3072"

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }
}

resource "aws_ecs_service" "c8-annie-trucks-dashboard-terraform" {
  name             = "c8-annie-trucks-dashboard-terraform"
  cluster          = resource.aws_ecs_cluster.c8-annie-trucks-terraform-cluster.arn
  task_definition  = resource.aws_ecs_task_definition.c8-annie-dashboard-task-terraform.arn
  launch_type      = "FARGATE"
  platform_version = "LATEST"

  network_configuration {
    subnets          = ["subnet-03b1a3e1075174995", "subnet-0667517a2a13e2a6b", "subnet-0cec5bdb9586ed3c4"]
    security_groups  = ["sg-0071f20861ba8ecfb"]
    assign_public_ip = true
  }

  desired_count = 1
}