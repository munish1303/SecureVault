$ErrorActionPreference = 'Stop'

$workspace = Resolve-Path '.'
$srcDir = Join-Path $workspace 'Project_Report_Build'
$baseDir = Join-Path $workspace '.report_ref\unzipped'
$contentPath = Join-Path $workspace 'Project_Report_Content.md'
$outputDocx = Join-Path $workspace 'Secure_Vault_Project_Report.docx'

if (Test-Path $srcDir) { Remove-Item $srcDir -Recurse -Force }
Copy-Item $baseDir $srcDir -Recurse

$baseXml = [xml](Get-Content (Join-Path $baseDir 'word\document.xml'))
$ns = New-Object System.Xml.XmlNamespaceManager($baseXml.NameTable)
$ns.AddNamespace('w','http://schemas.openxmlformats.org/wordprocessingml/2006/main')
$sectPr = $baseXml.SelectSingleNode('//w:body/w:sectPr', $ns).OuterXml

function Escape-Xml([string]$text) {
    $text = $text -replace '&', '&amp;'
    $text = $text -replace '<', '&lt;'
    $text = $text -replace '>', '&gt;'
    return $text
}

function Make-Paragraph([string]$text, [string]$style = '') {
    $escaped = Escape-Xml $text
    if ([string]::IsNullOrWhiteSpace($style)) {
        return "<w:p><w:r><w:t xml:space='preserve'>$escaped</w:t></w:r></w:p>"
    }
    return "<w:p><w:pPr><w:pStyle w:val='$style'/></w:pPr><w:r><w:t xml:space='preserve'>$escaped</w:t></w:r></w:p>"
}

$lines = Get-Content $contentPath
$paragraphs = New-Object System.Collections.Generic.List[string]
$firstTitleUsed = $false
foreach ($line in $lines) {
    if ($line.Trim() -eq '') { continue }
    if (-not $firstTitleUsed) {
        $paragraphs.Add((Make-Paragraph $line 'Title'))
        $firstTitleUsed = $true
        continue
    }
    if ($line.StartsWith('### ')) {
        $paragraphs.Add((Make-Paragraph ($line.Substring(4)) 'Heading2'))
        continue
    }
    if ($line.StartsWith('## ')) {
        $paragraphs.Add((Make-Paragraph ($line.Substring(3)) 'Heading1'))
        continue
    }
    $paragraphs.Add((Make-Paragraph $line))
}

$documentXml = @"
<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<w:document xmlns:wpc='http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas' xmlns:cx='http://schemas.microsoft.com/office/drawing/2014/chartex' xmlns:cx1='http://schemas.microsoft.com/office/drawing/2015/9/8/chartex' xmlns:cx2='http://schemas.microsoft.com/office/drawing/2015/10/21/chartex' xmlns:cx3='http://schemas.microsoft.com/office/drawing/2016/5/9/chartex' xmlns:cx4='http://schemas.microsoft.com/office/drawing/2016/5/10/chartex' xmlns:cx5='http://schemas.microsoft.com/office/drawing/2016/5/11/chartex' xmlns:cx6='http://schemas.microsoft.com/office/drawing/2016/5/12/chartex' xmlns:cx7='http://schemas.microsoft.com/office/drawing/2016/5/13/chartex' xmlns:cx8='http://schemas.microsoft.com/office/drawing/2016/5/14/chartex' xmlns:mc='http://schemas.openxmlformats.org/markup-compatibility/2006' xmlns:aink='http://schemas.microsoft.com/office/drawing/2016/ink' xmlns:am3d='http://schemas.microsoft.com/office/drawing/2017/model3d' xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:oel='http://schemas.microsoft.com/office/2019/extlst' xmlns:r='http://schemas.openxmlformats.org/officeDocument/2006/relationships' xmlns:m='http://schemas.openxmlformats.org/officeDocument/2006/math' xmlns:v='urn:schemas-microsoft-com:vml' xmlns:wp14='http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing' xmlns:wp='http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing' xmlns:w10='urn:schemas-microsoft-com:office:word' xmlns:w='http://schemas.openxmlformats.org/wordprocessingml/2006/main' xmlns:w14='http://schemas.microsoft.com/office/word/2010/wordml' xmlns:w15='http://schemas.microsoft.com/office/word/2012/wordml' xmlns:w16cex='http://schemas.microsoft.com/office/word/2018/wordml/cex' xmlns:w16cid='http://schemas.microsoft.com/office/word/2016/wordml/cid' xmlns:w16='http://schemas.microsoft.com/office/word/2018/wordml' xmlns:w16du='http://schemas.microsoft.com/office/word/2023/wordml/word16du' xmlns:w16sdtdh='http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash' xmlns:w16sdtfl='http://schemas.microsoft.com/office/word/2024/wordml/sdtformatlock' xmlns:w16se='http://schemas.microsoft.com/office/word/2015/wordml/symex' xmlns:wpg='http://schemas.microsoft.com/office/word/2010/wordprocessingGroup' xmlns:wpi='http://schemas.microsoft.com/office/word/2010/wordprocessingInk' xmlns:wne='http://schemas.microsoft.com/office/word/2006/wordml' xmlns:wps='http://schemas.microsoft.com/office/word/2010/wordprocessingShape' mc:Ignorable='w14 w15 w16se w16cid w16 w16cex w16sdtdh w16sdtfl w16du wp14'>
  <w:body>
    $($paragraphs -join "`n    ")
    $sectPr
  </w:body>
</w:document>
"@

Set-Content -Path (Join-Path $srcDir 'word\document.xml') -Value $documentXml -Encoding UTF8

if (Test-Path $outputDocx) { Remove-Item $outputDocx -Force }
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($srcDir, $outputDocx)
Get-Item $outputDocx | Select-Object FullName,Length
