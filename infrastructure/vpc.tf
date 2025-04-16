# Create a VPC
resource "aws_vpc" "big-data-platform-team-3" {
  cidr_block       = "10.0.0.0/16"
  instance_tenancy = "default"

  tags = {
    Name = "main"
  }
}

#Public subnet

resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.big-data-platform-team-3.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "Main"
  }
}

# Internet Gateway

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.big-data-platform-team-3.id

  tags = {
    Name = "main"
  }
}


# Route Table

resource "aws_route_table" "route_table" {
  vpc_id = aws_vpc.big-data-platform-team-3.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "main"
  }
}

# Subnet to route table association

resource "aws_route_table_association" "public_association" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.route_table.id
}