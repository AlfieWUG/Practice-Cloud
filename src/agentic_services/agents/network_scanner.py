"""
Network Scanner Agent for Nagarro Agentic Services Platform
Discovers network topology, identifies servers, services, and open ports
"""

import logging
from typing import Dict, Any, Optional, List

from agentic_services.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class NetworkScannerAgent(BaseAgent):
    """
    Network Scanner Agent - Discovers network infrastructure
    
    Responsibilities:
    - Map network topology (subnets, gateways, routes)
    - Identify all servers and their IP addresses
    - Scan open ports and identify running services
    - Detect service versions and configurations
    - Identify potential vulnerabilities
    - Generate comprehensive network inventory
    """
    
    SYSTEM_PROMPT = """You are a Network Scanner Agent specialized in discovering and analyzing network infrastructure.

Your tasks:
1. Analyze the target network range and scan parameters
2. Identify network topology (subnets, gateways, routing)
3. Discover all active servers and their IP addresses
4. Scan open ports on discovered servers
5. Identify running services and their versions
6. Detect service configurations (SSL, authentication, etc.)
7. Flag potential security vulnerabilities
8. Generate comprehensive network inventory

Return structured JSON with:
- network_topology: object with subnets, gateways, routes
- discovered_servers: array of server objects with hostname, ip_address, os, open_ports
- services: array of service objects with name, port, version, server, configuration
- vulnerabilities: array of identified security issues (optional)
- total_servers: integer count
- total_services: integer count
- total_open_ports: integer count (optional)
- scan_status: string (completed/partial/failed)
- message: string with additional information (optional)

Be thorough and accurate. Include all relevant technical details."""

    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(agent_id)
        self.agent_type = "network_scanner"
        self.scan_results: Optional[Dict[str, Any]] = None
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute network scan
        
        Args:
            task: Must contain:
                - project_id: Unique project identifier
                - target_network: Network range to scan (CIDR notation)
                - scan_type: Type of scan (optional: comprehensive, port_scan, service_identification)
                - port_range: Port range to scan (optional, e.g., "1-65535")
                - credentials: Authentication credentials for deeper scanning (optional)
                - include_vulnerabilities: Whether to scan for vulnerabilities (optional)
        
        Returns:
            Network scan results with discovered servers, services, and topology
        """
        try:
            # Validate inputs
            self.validate_task(task, ['project_id', 'target_network'])
            
            project_id = task['project_id']
            target_network = task['target_network']
            scan_type = task.get('scan_type', 'comprehensive')
            port_range = task.get('port_range', '1-1024')
            credentials = task.get('credentials')
            include_vulnerabilities = task.get('include_vulnerabilities', False)
            
            logger.info(f"Starting network scan for project: {project_id}, network: {target_network}")
            
            # Emit start event
            await self.emit_event(
                event_type='network_scan.started',
                detail={
                    'project_id': project_id,
                    'target_network': target_network,
                    'scan_type': scan_type
                },
                project_id=project_id
            )
            
            # Perform network scan
            scan_results = await self._perform_network_scan(
                target_network=target_network,
                scan_type=scan_type,
                port_range=port_range,
                credentials=credentials,
                include_vulnerabilities=include_vulnerabilities
            )
            
            # Enrich with metadata
            scan_results['project_id'] = project_id
            scan_results['agent_id'] = self.agent_id
            scan_results['status'] = 'completed'
            scan_results['target_network'] = target_network
            scan_results['scan_type'] = scan_type
            
            # Store scan results in S3
            s3_uri = await self.store_data(
                project_id=project_id,
                data_type='network_scan',
                data=scan_results
            )
            
            scan_results['s3_uri'] = s3_uri
            
            # Save state
            await self.save_state(
                project_id=project_id,
                state={'last_scan': s3_uri}
            )
            
            # Emit completion event
            await self.emit_event(
                event_type='network_scan.completed',
                detail={
                    'project_id': project_id,
                    's3_uri': s3_uri,
                    'total_servers': scan_results.get('total_servers', 0),
                    'total_services': scan_results.get('total_services', 0)
                },
                project_id=project_id
            )
            
            logger.info(
                f"Network scan completed for project: {project_id}, "
                f"found {scan_results.get('total_servers', 0)} servers"
            )
            self.scan_results = scan_results
            
            return scan_results
            
        except Exception as e:
            logger.error(f"Network scan failed: {e}", exc_info=True)
            
            # Emit failure event
            await self.emit_event(
                event_type='network_scan.failed',
                detail={
                    'project_id': task.get('project_id'),
                    'target_network': task.get('target_network'),
                    'error': str(e)
                },
                project_id=task.get('project_id')
            )
            
            raise
    
    async def _perform_network_scan(
        self,
        target_network: str,
        scan_type: str = 'comprehensive',
        port_range: str = '1-1024',
        credentials: Optional[Dict[str, Any]] = None,
        include_vulnerabilities: bool = False
    ) -> Dict[str, Any]:
        """
        Perform network scan using AI
        
        Args:
            target_network: Network range to scan (CIDR)
            scan_type: Type of scan to perform
            port_range: Port range for scanning
            credentials: Optional authentication credentials
            include_vulnerabilities: Whether to include vulnerability scanning
            
        Returns:
            Structured network scan data
        """
        # Build comprehensive prompt
        creds_section = ""
        if credentials:
            creds_section = f"""
AUTHENTICATION:
- Credentials provided for authenticated scanning
- Username: {credentials.get('username', 'N/A')}
- Access type: {credentials.get('access_type', 'SSH key')}
"""
        
        vuln_section = ""
        if include_vulnerabilities:
            vuln_section = """
VULNERABILITY SCANNING:
- Identify outdated service versions
- Flag known CVEs
- Assess security configurations
- Report potential security issues
"""
        
        prompt = f"""Perform a {scan_type} network scan on the following network:

TARGET NETWORK: {target_network}
PORT RANGE: {port_range}
SCAN TYPE: {scan_type}

{creds_section}
{vuln_section}

Discover:
1. Network topology (subnets, gateways, routing)
2. All active servers (hostname, IP, OS)
3. Open ports on each server
4. Running services and versions
5. Service configurations (SSL, auth, etc.)
6. Dependencies between services

Provide comprehensive network inventory in JSON format as specified."""
        
        # Invoke AI for network analysis
        ai_response = await self.invoke_ai(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.2  # Lower temperature for accurate network discovery
        )
        
        # Parse AI response
        import json
        try:
            scan_data = json.loads(ai_response)
        except json.JSONDecodeError:
            # Fallback: extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', ai_response, re.DOTALL)
            if json_match:
                scan_data = json.loads(json_match.group(1))
            else:
                # Last resort: create structured response from text
                scan_data = {
                    'raw_scan': ai_response,
                    'network_topology': {},
                    'discovered_servers': [],
                    'services': [],
                    'total_servers': 0,
                    'total_services': 0,
                    'scan_status': 'completed',
                    'message': 'Scan completed with limited structure'
                }
        
        return scan_data
    
    async def get_scan_summary(self, project_id: str) -> Optional[str]:
        """
        Get a text summary of the network scan results
        
        Args:
            project_id: Project identifier
            
        Returns:
            Human-readable summary or None if not available
        """
        if not self.scan_results:
            # Try to load from state
            state = await self.load_state(project_id)
            if not state or 'last_scan' not in state:
                return None
            
            # Load from S3
            scan_data = await self.load_data(state['last_scan'])
            self.scan_results = scan_data
        
        # Generate summary
        total_servers = self.scan_results.get('total_servers', 0)
        total_services = self.scan_results.get('total_services', 0)
        network = self.scan_results.get('target_network', 'N/A')
        
        servers = self.scan_results.get('discovered_servers', [])
        services = self.scan_results.get('services', [])
        
        summary = f"""Network Scan Summary:
Target Network: {network}
Discovered Servers: {total_servers}
Running Services: {total_services}

Top Servers:
"""
        for i, server in enumerate(servers[:5], 1):
            hostname = server.get('hostname', 'unknown')
            ip = server.get('ip_address', 'N/A')
            ports = len(server.get('open_ports', []))
            summary += f"{i}. {hostname} ({ip}) - {ports} open ports\n"
        
        if services:
            summary += "\nTop Services:\n"
            for i, service in enumerate(services[:5], 1):
                name = service.get('name', 'unknown')
                port = service.get('port', 'N/A')
                version = service.get('version', 'unknown')
                summary += f"{i}. {name}:{port} v{version}\n"
        
        vulnerabilities = self.scan_results.get('vulnerabilities', [])
        if vulnerabilities:
            summary += f"\n⚠️  {len(vulnerabilities)} potential vulnerabilities identified"
        
        return summary
