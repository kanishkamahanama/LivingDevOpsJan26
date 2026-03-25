# network.tf

# VPC

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = var.vpc_name
  }
}

# CIDC planning
# public ->  "10.0.1.0/24", "10.0.2.0/24"
# private -> "10.0.3.0/24", "10.0.4.0/24"
#rds -> "10.0.5.0/24", "10.0.6.0/24"

# 2 public subnets
resource "aws_subnet" "public1" {
  # dependency type Implicit
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = var.primary_az

  tags = {
    # String interpolation
    Name = "${var.vpc_name}-public1"
  }
}

resource "aws_subnet" "public2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  map_public_ip_on_launch = true
  availability_zone       = var.secondary_az

  tags = {
    Name = "${var.vpc_name}-public12"
  }
}

# 1 Route table for public subnets

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "public RT"
  }
}

# Internet Gateway

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "IGW"
  }
}

# Add public subnets to route table

# implicit dependency on aws_subnet.public1 and aws_route_table.public
resource "aws_route_table_association" "a" {
  subnet_id      = aws_subnet.public1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "b" {
  subnet_id      = aws_subnet.public2.id
  route_table_id = aws_route_table.public.id
}

# Add a route to internet gateway in route table

# NAT Gateway (only 1 for cost saving)

resource "aws_nat_gateway" "primary" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public1.id

  tags = {
    Name = "gw NAT"
  }

  # To ensure proper ordering, it is recommended to add an explicit dependency
  # on the Internet Gateway for the VPC.

  # explicit dependency on IGW to ensure it is created before the NAT gateway
  depends_on = [aws_internet_gateway.igw, aws_route_table.public]
}

# Elastic IP for NAT Gateway

resource "aws_eip" "nat" {

}


# 2 private subnets
resource "aws_subnet" "private1" {
  # dependency type Implicit
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.3.0/24"
  map_public_ip_on_launch = false
  availability_zone       = var.primary_az

  tags = {
    # String interpolation
    Name = "${var.vpc_name}-private1"
  }
}

resource "aws_subnet" "private2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.4.0/24"
  map_public_ip_on_launch = false
  availability_zone       = var.secondary_az

  tags = {
    Name = "${var.vpc_name}-private2"
  }
}

# 1 Route table for privae subnets

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "private RT"
  }
}

resource "aws_route" "r" {
  route_table_id         = aws_route_table.private.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.primary.id
}

# Add private subnets to route table

# implicit dependency on aws_subnet.private1 and aws_route_table.private
resource "aws_route_table_association" "c" {
  subnet_id      = aws_subnet.private1.id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "d" {
  subnet_id      = aws_subnet.private2.id
  route_table_id = aws_route_table.private.id
}

# Add a route to NAT gateway in route table


# 2 RDS subnet

resource "aws_subnet" "rds1" {
  # dependency type Implicit
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.5.0/24"
  map_public_ip_on_launch = false
  availability_zone       = var.primary_az

  tags = {
    # String interpolation
    Name = "${var.vpc_name}-rds1"
  }
}

resource "aws_subnet" "rds2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.6.0/24"
  map_public_ip_on_launch = false
  availability_zone       = var.secondary_az

  tags = {
    Name = "${var.vpc_name}-rds2"
  }
}
