import os
import xml.etree.ElementTree as ET  # nosec B405


def create_aws_icon_drawio_xml():
    mxfile = ET.Element(
        "mxfile",
        {
            "host": "app.diagrams.net",
            "modified": "2026-07-24T23:36:00.000Z",
            "agent": "Antigravity Assistant",
            "version": "21.6.8",
            "type": "device",
        },
    )

    diagram = ET.SubElement(
        mxfile,
        "diagram",
        {
            "id": "crown-corridor-aws-icons",
            "name": "Crown Corridor Official AWS Icons Architecture",
        },
    )

    model = ET.SubElement(
        diagram,
        "mxGraphModel",
        {
            "dx": "1800",
            "dy": "1300",
            "grid": "1",
            "gridSize": "10",
            "guides": "1",
            "tooltips": "1",
            "connect": "1",
            "arrows": "1",
            "fold": "1",
            "page": "1",
            "pageScale": "1",
            "pageWidth": "1900",
            "pageHeight": "1400",
            "math": "0",
            "shadow": "0",
        },
    )

    root = ET.SubElement(model, "root")

    # Base cells required by Draw.io
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

    def add_node(cell_id, value, style, x, y, width, height, parent="1"):
        cell = ET.SubElement(
            root,
            "mxCell",
            {"id": cell_id, "value": value, "style": style, "vertex": "1", "parent": parent},
        )
        ET.SubElement(
            cell,
            "mxGeometry",
            {
                "x": str(x),
                "y": str(y),
                "width": str(width),
                "height": str(height),
                "as": "geometry",
            },
        )
        return cell

    def add_edge(edge_id, value, style, source, target, parent="1"):
        cell = ET.SubElement(
            root,
            "mxCell",
            {
                "id": edge_id,
                "value": value,
                "style": style,
                "edge": "1",
                "parent": parent,
                "source": source,
                "target": target,
            },
        )
        ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
        return cell

    # --- Official AWS4 Icon & Group Styles ---
    aws_group = "shape=mxgraph.aws4.group;grType={grtype};strokeColor={stroke};fillColor={fill};fontColor={font};verticalAlign=top;align=left;spacingLeft=15;spacingTop=10;fontSize=14;fontStyle=1;"
    aws_icon = "sketch=0;outlineConnect=0;fontColor={font};gradientColor=none;fillColor={fill};strokeColor=none;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=1;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.{shape};"
    edge_style = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor={stroke};strokeWidth=2;fontSize=11;fontColor={font};"

    # --- 1. Client Layer ---
    add_node(
        "clients",
        "Web / Mobile Clients\n(Users / Investors)",
        aws_icon.format(shape="user", fill="#232F3E", font="#FFFFFF"),
        60,
        470,
        70,
        70,
    )

    # --- 2. AWS Cloud Region Container ---
    add_node(
        "aws_cloud",
        "☁️ AWS Cloud Region (us-east-1)",
        aws_group.format(grtype="region", stroke="#FF9900", fill="#1A222F", font="#FF9900"),
        200,
        40,
        1650,
        1220,
    )

    # --- 3. Edge Security & Delivery Container ---
    add_node(
        "edge_layer",
        "🛡️ Edge Security & Global Content Delivery",
        aws_group.format(grtype="noGroup", stroke="#E7157B", fill="#242F3D", font="#E7157B"),
        240,
        90,
        1570,
        200,
    )

    add_node(
        "waf",
        "AWS WAF Web ACL\n(OWASP Top 10)",
        aws_icon.format(shape="waf", fill="#E7157B", font="#FFFFFF"),
        280,
        140,
        68,
        68,
    )

    add_node(
        "cloudfront",
        "Amazon CloudFront CDN\n(TLS 1.3)",
        aws_icon.format(shape="cloudfront", fill="#ED7100", font="#FFFFFF"),
        550,
        140,
        68,
        68,
    )

    add_node(
        "s3_web",
        "Amazon S3 Static Web UI\n(Private OAC, KMS)",
        aws_icon.format(shape="s3_bucket", fill="#E05243", font="#FFFFFF"),
        850,
        140,
        68,
        68,
    )

    add_node(
        "apigw",
        "Amazon API Gateway v2\n(JWT Auth, Throttling)",
        aws_icon.format(shape="api_gateway", fill="#ED7100", font="#FFFFFF"),
        1150,
        140,
        68,
        68,
    )

    add_node(
        "cognito",
        "Amazon Cognito\n(JWT Tokens)",
        aws_icon.format(shape="cognito", fill="#ED7100", font="#FFFFFF"),
        1450,
        140,
        68,
        68,
    )

    # --- 4. VPC Network Container ---
    add_node(
        "vpc",
        "🔒 Amazon VPC (10.0.0.0/16) — Multi-AZ Isolated Network",
        aws_group.format(grtype="vpc", stroke="#8C4FFF", fill="#162536", font="#8C4FFF"),
        240,
        320,
        1570,
        690,
    )

    # Public Subnets Container
    add_node(
        "pub_subnets",
        "🌐 Public Subnets (AZ1: 10.0.1.0/24 | AZ2: 10.0.2.0/24)",
        aws_group.format(grtype="subnet", stroke="#00A4A6", fill="#1F3347", font="#00A4A6"),
        270,
        370,
        1510,
        120,
    )

    add_node(
        "igw",
        "Internet Gateway",
        aws_icon.format(shape="internet_gateway", fill="#8C4FFF", font="#FFFFFF"),
        320,
        405,
        60,
        60,
    )

    add_node(
        "alb",
        "Application Load Balancer (ALB)\n(Header Dropping)",
        aws_icon.format(shape="application_load_balancer", fill="#8C4FFF", font="#FFFFFF"),
        850,
        405,
        68,
        68,
    )

    add_node(
        "nat",
        "NAT Gateways",
        aws_icon.format(shape="nat_gateway", fill="#8C4FFF", font="#FFFFFF"),
        1650,
        405,
        60,
        60,
    )

    # Private Compute Subnets Container
    add_node(
        "priv_compute_subnets",
        "⚡ Private Compute Subnets (AZ1: 10.0.10.0/24 | AZ2: 10.0.20.0/24)",
        aws_group.format(grtype="subnet", stroke="#00A4A6", fill="#1A2D3E", font="#00A4A6"),
        270,
        510,
        1510,
        220,
    )

    add_node(
        "fastapi",
        "ECS Fargate - FastAPI Container\n(Desired Count = 2)",
        aws_icon.format(shape="ecs", fill="#FF9900", font="#FFFFFF"),
        450,
        570,
        68,
        68,
    )

    add_node(
        "typesense",
        "ECS Fargate - Typesense Search\n(Internal DNS :8108)",
        aws_icon.format(shape="ecs", fill="#FF9900", font="#FFFFFF"),
        900,
        570,
        68,
        68,
    )

    add_node(
        "efs",
        "Amazon EFS Storage\n(Encrypted Index Volume)",
        aws_icon.format(shape="efs", fill="#2E27AD", font="#FFFFFF"),
        1400,
        570,
        68,
        68,
    )

    # Private Database Subnets Container
    add_node(
        "priv_db_subnets",
        "🗄️ Private Database Subnets (AZ1: 10.0.100.0/24 | AZ2: 10.0.200.0/24)",
        aws_group.format(grtype="subnet", stroke="#00A4A6", fill="#1F2A38", font="#00A4A6"),
        270,
        750,
        1510,
        230,
    )

    add_node(
        "rds",
        "Amazon RDS PostgreSQL 15.4 PostGIS\n(Storage Encrypted, Multi-AZ)",
        aws_icon.format(shape="rds", fill="#2E27AD", font="#FFFFFF"),
        850,
        810,
        68,
        68,
    )

    # --- 5. Security & Auditing Layer (Bottom) ---
    add_node(
        "sec_layer",
        "🔐 Security, Auditing, Monitoring & Event Layer",
        aws_group.format(grtype="noGroup", stroke="#00A4A6", fill="#222B38", font="#00A4A6"),
        240,
        1030,
        1570,
        200,
    )

    add_node(
        "kms",
        "AWS KMS\n(Auto-Rotating Key)",
        aws_icon.format(shape="kms", fill="#ED7100", font="#FFFFFF"),
        280,
        1080,
        68,
        68,
    )

    add_node(
        "secrets",
        "Secrets Manager\n(DB & API Keys)",
        aws_icon.format(shape="secrets_manager", fill="#ED7100", font="#FFFFFF"),
        520,
        1080,
        68,
        68,
    )

    add_node(
        "cloudtrail",
        "AWS CloudTrail\n(Log Validation)",
        aws_icon.format(shape="cloudtrail", fill="#ED7100", font="#FFFFFF"),
        760,
        1080,
        68,
        68,
    )

    add_node(
        "guardduty",
        "GuardDuty & Security Hub\n(Threat Detection)",
        aws_icon.format(shape="guardduty", fill="#ED7100", font="#FFFFFF"),
        1000,
        1080,
        68,
        68,
    )

    add_node(
        "eventbridge",
        "Amazon EventBridge\n(Weekly ETL Cron)",
        aws_icon.format(shape="eventbridge", fill="#ED7100", font="#FFFFFF"),
        1240,
        1080,
        68,
        68,
    )

    add_node(
        "sns",
        "Amazon SNS Topic\n(Email Alerts)",
        aws_icon.format(shape="sns", fill="#ED7100", font="#FFFFFF"),
        1480,
        1080,
        68,
        68,
    )

    # --- Connections / Edges ---
    add_edge(
        "e1",
        "HTTPS / Port 443",
        edge_style.format(stroke="#FF9900", font="#FFFFFF"),
        "clients",
        "waf",
    )
    add_edge(
        "e2", "Inspection", edge_style.format(stroke="#FF9900", font="#FFFFFF"), "waf", "cloudfront"
    )
    add_edge(
        "e3",
        "Private OAC Read",
        edge_style.format(stroke="#7AA116", font="#FFFFFF"),
        "cloudfront",
        "s3_web",
    )
    add_edge(
        "e4",
        "API Proxy Request",
        edge_style.format(stroke="#E7157B", font="#FFFFFF"),
        "cloudfront",
        "apigw",
    )
    add_edge(
        "e5",
        "JWT Authorizer",
        edge_style.format(stroke="#C925D1", font="#FFFFFF"),
        "apigw",
        "cognito",
    )
    add_edge(
        "e6", "VPCLink Routing", edge_style.format(stroke="#8C4FFF", font="#FFFFFF"), "apigw", "alb"
    )
    add_edge(
        "e7",
        "Target Group Forward",
        edge_style.format(stroke="#FF9900", font="#FFFFFF"),
        "alb",
        "fastapi",
    )
    add_edge(
        "e8",
        "Internal Search Query (:8108)",
        edge_style.format(stroke="#C925D1", font="#FFFFFF"),
        "fastapi",
        "typesense",
    )
    add_edge(
        "e9",
        "PostGIS Spatial Query (:5432)",
        edge_style.format(stroke="#D55200", font="#FFFFFF"),
        "fastapi",
        "rds",
    )
    add_edge(
        "e10",
        "Mount Volume",
        edge_style.format(stroke="#2E27AD", font="#FFFFFF"),
        "typesense",
        "efs",
    )
    add_edge(
        "e11",
        "Trigger Job",
        edge_style.format(stroke="#ED7100", font="#FFFFFF"),
        "eventbridge",
        "fastapi",
    )
    add_edge(
        "e12",
        "Send Alert",
        edge_style.format(stroke="#ED7100", font="#FFFFFF"),
        "eventbridge",
        "sns",
    )

    # Write files
    xml_str = ET.tostring(mxfile, encoding="utf-8")

    os.makedirs("docs", exist_ok=True)
    os.makedirs("terraform", exist_ok=True)

    with open("docs/architecture.drawio", "wb") as f:
        f.write(xml_str)

    with open("terraform/architecture.drawio", "wb") as f:
        f.write(xml_str)

    print(
        "Official AWS Icons Draw.io XML successfully created at docs/architecture.drawio & terraform/architecture.drawio"
    )


if __name__ == "__main__":
    create_aws_icon_drawio_xml()
