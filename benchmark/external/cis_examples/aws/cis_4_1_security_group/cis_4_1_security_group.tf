# CIS AWS 4.1 - Security Group Unrestricted Ingress

resource "aws_security_group" "allow_all" {
  name        = "allow_all_ssh"
  description = "Allow inbound SSH traffic"

  ingress {
    description      = "SSH from anywhere"
    from_port        = 22
    to_port          = 22
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}
