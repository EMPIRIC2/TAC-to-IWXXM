<?xml version="1.0" encoding="UTF-8"?>

<!--
	XSLT to output an XSLT fragment for inclusion in a GML post-processing script:
		(1) Copy notes from and reflect use="required" and nillable="true" in UML class attributes to/in their XSD counterparts
		(2) Reflect nillable="true" in UML association targets in their XSD counterparts
		(3) Remeove elements in XSD counterparts of UML classes of stereotype <<codeList>> - Disabled
		(4) Add extension elements to XSD counterparts of non-abstract UML classes
		(5) Add serialization of tagged value on quantity assigned to a UML attribute to a UML class
		(6) Correct incorrectly transformed stereotype <<union>>
                (7) Add elements in XSD counterparts of UML classes of stereotype <<enumeration>> to allow it to be used globally

	Created by B.L. Choy (blchoy.hko@gmail.com).  First created on 9 July 2016.  Last updated on 12 May 2021.

	Tested with the following:
		(1) XMI: Created by EA 12.1 Build 1224 with UML 1.3 (XMI 1.1)
		(2) XSLT processor: Saxon-HE 9.7.0.15N
-->

<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:lsx="foo.bar" xmlns:UML="omg.org/UML1.3" exclude-result-prefixes="UML"> 
	<xsl:output method="xml" encoding="UTF-8" indent="yes"/>
	<xsl:namespace-alias stylesheet-prefix="lsx" result-prefix="xsl"/>
	<xsl:strip-space elements="*"/>

	<xsl:template match="/XMI">
		<lsx:stylesheet version="2.0" exclude-result-prefixes=" xs">
			<xsl:apply-templates select="@*|node()"/>
		</lsx:stylesheet>
	</xsl:template>

	<xsl:template match="//UML:Class/UML:Classifier.feature/UML:Attribute">

		<xsl:param name="typeName_xsl" select="./UML:ModelElement.taggedValue/UML:TaggedValue[@tag='type']/@value"/>
	
		<!-- Remove @type to prepare for the addition of "@nilReason" -->
		<xsl:if test="./UML:ModelElement.taggedValue/UML:TaggedValue[@tag='nillable']/@value = 'true'">

			<xsl:if test="not($typeName_xsl = 'AngleWithNilReason') and not($typeName_xsl = 'LengthWithNilReason') and not($typeName_xsl = 'DistanceWithNilReason') and not($typeName_xsl = 'MeasureWithNilReason') and not($typeName_xsl = 'VelocityWithNilReason') and not($typeName_xsl = 'StringWithNilReason') and not($typeName_xsl = 'AirspaceVolume') and not($typeName_xsl = 'TM_Instant') and not(//UML:Class[@name=$typeName_xsl]/UML:ModelElement.stereotype/UML:Stereotype/@name = 'featureType') and not(//UML:Class[@name=$typeName_xsl]/UML:ModelElement.stereotype/UML:Stereotype/@name = 'type') and not(//UML:Class[@name=$typeName_xsl]/UML:ModelElement.stereotype/UML:Stereotype/@name = 'codeList') and not(//UML:Class[@name=$typeName_xsl]/UML:ModelElement.stereotype/UML:Stereotype/@name = 'enumeration') and not(//UML:Class[@name=$typeName_xsl]/UML:ModelElement.stereotype/UML:Stereotype/@name = 'union') and exists(//UML:Class[@name=$typeName_xsl]/UML:ModelElement.stereotype/UML:Stereotype/@name)">

				<lsx:template xmlns:xs="http://www.w3.org/2001/XMLSchema" match="xs:complexType[@name='{../../@name}Type']//xs:sequence/xs:element[@name='{@name}']/@type"/>

			</xsl:if>

		</xsl:if>

		<lsx:template xmlns:xs="http://www.w3.org/2001/XMLSchema" match="xs:complexType[@name='{../../@name}Type']//xs:sequence/xs:element[@name='{@name}']">
			<lsx:param name="typeName" select="@type"/>
			<lsx:element name="{{local-name()}}">

				<xsl:if test="./UML:ModelElement.taggedValue/UML:TaggedValue[@tag='nillable']/@value = 'true'">

					<!-- Add 'nillable="true"' and "@nilReason" to nillable attributes (EA GML transformation Issue 3) -->
					<lsx:attribute name="nillable">
						<lsx:value-of select="'true'"/>
					</lsx:attribute>

				</xsl:if>

				<xsl:choose>

					<xsl:when test="(./UML:ModelElement.taggedValue/UML:TaggedValue[@tag='quantity']/@value != '') and ((./UML:ModelElement.taggedValue/UML:TaggedValue[@tag='xsdAsAttribute']/@value = 'false') or not(./UML:ModelElement.taggedValue/UML:TaggedValue[@tag='xsdAsAttribute'])) and not(../../UML:ModelElement.stereotype/UML:Stereotype/@name = 'type') and not(../../UML:ModelElement.stereotype/UML:Stereotype/@name = 'dataType') and exists(../../UML:ModelElement.stereotype/UML:Stereotype/@name)">

						<lsx:copy-of select="@*"/>

						<!-- Add quantity to attributes (EA GML transformation Issue 9) -->
						<lsx:element name="annotation">
							<lsx:copy-of select='./xs:annotation/@*'/>
							<lsx:apply-templates select="./xs:annotation/*"/>
							<lsx:element name="appinfo">
								<lsx:element name="quantity">
									<xsl:value-of select="./UML:ModelElement.taggedValue/UML:TaggedValue[@tag='quantity']/@value"/>
								</lsx:element>
							</lsx:element>
						</lsx:element>

						<lsx:apply-templates select="./*[not(name() = 'xs:annotation')]"/>

					</xsl:when>

					<xsl:otherwise>

						<lsx:apply-templates select="@*|node()"/>

					</xsl:otherwise>

				</xsl:choose>

				<xsl:if test="./UML:ModelElement.taggedValue/UML:TaggedValue[@tag='nillable']/@value = 'true'">

					<!-- Add "@nilReason" with manual exceptions to those (specially defined) classes and stereotypes which already have it through inheritation -->
					<xsl:if test="not($typeName_xsl = 'AngleWithNilReason') and not($typeName_xsl = 'LengthWithNilReason') and not($typeName_xsl = 'DistanceWithNilReason') and not($typeName_xsl = 'MeasureWithNilReason') and not($typeName_xsl = 'VelocityWithNilReason') and not($typeName_xsl = 'StringWithNilReason') and not($typeName_xsl = 'AirspaceVolume') and not($typeName_xsl = 'TM_Instant') and not(//UML:Class[@name=$typeName_xsl]/UML:ModelElement.stereotype/UML:Stereotype/@name = 'featureType') and not(//UML:Class[@name=$typeName_xsl]/UML:ModelElement.stereotype/UML:Stereotype/@name = 'type') and not(//UML:Class[@name=$typeName_xsl]/UML:ModelElement.stereotype/UML:Stereotype/@name = 'codeList') and not(//UML:Class[@name=$typeName_xsl]/UML:ModelElement.stereotype/UML:Stereotype/@name = 'enumeration') and not(//UML:Class[@name=$typeName_xsl]/UML:ModelElement.stereotype/UML:Stereotype/@name = 'union') and exists(//UML:Class[@name=$typeName_xsl]/UML:ModelElement.stereotype/UML:Stereotype/@name)">

						<lsx:element name="complexType">
							<lsx:element name="complexContent">
								<lsx:element name="extension">
									<lsx:attribute name="base">
										<lsx:value-of select="$typeName"/>
									</lsx:attribute>
									<lsx:element name="attribute">
										<lsx:attribute name="name">
											<lsx:value-of select="'nilReason'"/>
										</lsx:attribute>
										<lsx:attribute name="type">
											<lsx:value-of select="'gml:NilReasonType'"/>
										</lsx:attribute>
									</lsx:element>
								</lsx:element>
							</lsx:element>
						</lsx:element>

					</xsl:if>

				</xsl:if>

			</lsx:element>
		</lsx:template>

		<!-- For those UML attributes serialized as XML attributes (Tagged value xsdAsAttribute='true') -->
		<lsx:template xmlns:xs="http://www.w3.org/2001/XMLSchema" match="xs:complexType[@name='{../../@name}Type']//xs:attribute[@name='{@name}']">
			<lsx:element name="{{local-name()}}">

				<xsl:if test="not(./UML:ModelElement.taggedValue/UML:TaggedValue[@tag='stereotype']/@value = 'enum') and (./UML:ModelElement.taggedValue/UML:TaggedValue[@tag='lowerBound']/@value = '1') and (./UML:ModelElement.taggedValue/UML:TaggedValue[@tag='upperBound']/@value = '1')">

					<!-- Add 'use="required"' to mandatory attributes (EA GML transformation Issue 2) -->
					<lsx:attribute name="use">
						<lsx:value-of select="'required'"/>
					</lsx:attribute>

				</xsl:if>
	
				<lsx:apply-templates select='@*|node()'/>

				<!-- Add documentation to attributes (EA GML transformation Issue 6) -->
				<lsx:element name="annotation">
					<lsx:element name="documentation">
						<xsl:value-of select="./UML:ModelElement.taggedValue/UML:TaggedValue[@tag='description']/@value"/>
					</lsx:element>
				</lsx:element>

			</lsx:element>
		</lsx:template>

	</xsl:template>

	<xsl:template match="//UML:Association/UML:Association.connection">

		<xsl:param name="sourceClassId" select="./UML:AssociationEnd/UML:ModelElement.taggedValue/UML:TaggedValue[@tag='ea_end' and @value='source']/../../@type"/>
		<xsl:param name="sourceClassName" select="//UML:Class[@xmi.id=$sourceClassId]/@name"/>
		<xsl:param name="targetClassId" select="./UML:AssociationEnd/UML:ModelElement.taggedValue/UML:TaggedValue[@tag='ea_end' and @value='target']/../../@type"/>
		<xsl:param name="targetClassName" select="//UML:Class[@xmi.id=$targetClassId]/@name"/>
		<xsl:param name="targetRoleName" select="./UML:AssociationEnd/UML:ModelElement.taggedValue/UML:TaggedValue[@tag='ea_end' and @value='target']/../../@name"/>

		<xsl:if test="./UML:AssociationEnd/UML:ModelElement.taggedValue/UML:TaggedValue[@tag='ea_end' and @value='target']/../UML:TaggedValue[@tag='nillable']/@value = 'true'">

			<!-- Remove @type to prepare for the addition of "@nilReason" -->
			<xsl:if test="not($targetClassName = 'AngleWithNilReason') and not($targetClassName = 'LengthWithNilReason') and not($targetClassName = 'DistanceWithNilReason') and not($targetClassName = 'MeasureWithNilReason') and not($targetClassName = 'VelocityWithNilReason') and not($targetClassName = 'StringWithNilReason') and not($targetClassName = 'AirspaceVolume') and not($targetClassName = 'TM_Instant') and not(//UML:Class[@xmi.id=$targetClassId]/UML:ModelElement.stereotype/UML:Stereotype/@name = 'featureType') and not(//UML:Class[@xmi.id=$targetClassId]/UML:ModelElement.stereotype/UML:Stereotype/@name = 'type') and not(//UML:Class[@xmi.id=$targetClassId]/UML:ModelElement.stereotype/UML:Stereotype/@name = 'codeList') and not(//UML:Class[@xmi.id=$targetClassId]/UML:ModelElement.stereotype/UML:Stereotype/@name = 'enumeration') and not(//UML:Class[@xmi.id=$targetClassId]/UML:ModelElement.stereotype/UML:Stereotype/@name = 'union') and exists(//UML:Class[@xmi.id=$targetClassId]/UML:ModelElement.stereotype/UML:Stereotype/@name)">

				<lsx:template xmlns:xs="http://www.w3.org/2001/XMLSchema" match="xs:complexType[@name='{../../$sourceClassName}Type']//xs:sequence/xs:element[(@name='{$targetRoleName}' and '{$targetRoleName}' != '') or (@name='{$targetClassName}' and '{$targetClassName}' != '')]/@type"/>

			</xsl:if>
			
			<lsx:template xmlns:xs="http://www.w3.org/2001/XMLSchema" match="xs:complexType[@name='{../../$sourceClassName}Type']//xs:sequence/xs:element[(@name='{$targetRoleName}' and '{$targetRoleName}' != '') or (@name='{$targetClassName}' and '{$targetClassName}' != '')]">
				<lsx:param name="typeName" select="@type"/>
				<lsx:element name="{{local-name()}}">

					<!-- Add 'nillable="true"' and "@nilReason" to nillable association target roles (EA GML transformation Issue 3) -->
					<lsx:attribute name="nillable">
						<lsx:value-of select="'true'"/>
					</lsx:attribute>

					<lsx:apply-templates select='@*|node()'/>

					<!-- Add "@nilReason" with manual exceptions to those (specially defined) classes and stereotypes which already have it through inheritation -->
					<xsl:if test="not($targetClassName = 'AngleWithNilReason') and not($targetClassName = 'LengthWithNilReason') and not($targetClassName = 'DistanceWithNilReason') and not($targetClassName = 'MeasureWithNilReason') and not($targetClassName = 'VelocityWithNilReason') and not($targetClassName = 'StringWithNilReason') and not($targetClassName = 'AirspaceVolume') and not($targetClassName = 'TM_Instant') and not(//UML:Class[@xmi.id=$targetClassId]/UML:ModelElement.stereotype/UML:Stereotype/@name = 'featureType') and not(//UML:Class[@xmi.id=$targetClassId]/UML:ModelElement.stereotype/UML:Stereotype/@name = 'type') and not(//UML:Class[@xmi.id=$targetClassId]/UML:ModelElement.stereotype/UML:Stereotype/@name = 'codeList') and not(//UML:Class[@xmi.id=$targetClassId]/UML:ModelElement.stereotype/UML:Stereotype/@name = 'enumeration') and not(//UML:Class[@xmi.id=$targetClassId]/UML:ModelElement.stereotype/UML:Stereotype/@name = 'union') and exists(//UML:Class[@xmi.id=$targetClassId]/UML:ModelElement.stereotype/UML:Stereotype/@name)">

						<lsx:element name="complexType">
							<lsx:element name="complexContent">
								<lsx:element name="extension">
									<lsx:attribute name="base">
										<lsx:value-of select="$typeName"/>
									</lsx:attribute>
									<lsx:element name="attribute">
										<lsx:attribute name="name">
											<lsx:value-of select="'nilReason'"/>
										</lsx:attribute>
										<lsx:attribute name="type">
											<lsx:value-of select="'gml:NilReasonType'"/>
										</lsx:attribute>
									</lsx:element>
								</lsx:element>
							</lsx:element>
						</lsx:element>

					</xsl:if>

				</lsx:element>
			</lsx:template>

		</xsl:if>

	</xsl:template>

	<xsl:template match="//UML:Class/UML:ModelElement.stereotype">

		<xsl:param name="className" select="../@name"/>
		<xsl:param name="classID" select="../@xmi.id"/>

		<!-- Disabled to allow codeLists to be included in phenomenonProperty of MeteorologicalFeature -->
		<!-- <xsl:if test="./UML:Stereotype/@name = 'codeList'"> -->

			<!-- For UML classes of stereotype <<codeList>>, as their XSD counterparts are solely for inclusion as XSD attributes, only the types defined are required but not the element -->
			<!-- <lsx:template xmlns:xs="http://www.w3.org/2001/XMLSchema" match="xs:element[@name='{$className}']"/> -->

		<!-- </xsl:if> -->

		<xsl:if test="./UML:Stereotype/@name = 'union'">

			<!-- For UML classes of stereotype <<union>>, EA12 incorrectly transform it as it is a <<featureType>> introducing <extension base="gml:AbstractObjectType"> in which the GML type is non-existing -->
			<lsx:template xmlns:xs="http://www.w3.org/2001/XMLSchema" match="xs:complexType[@name='{$className}Type']">

				<lsx:element name="complexType">
					<lsx:attribute name="name">
						<lsx:value-of select="'{$className}Type'"/>
					</lsx:attribute>
					<lsx:apply-templates select='//xs:choice'/>
				</lsx:element>

			</lsx:template>

		</xsl:if>

		<xsl:if test="(./UML:Stereotype/@name = 'enumeration') and (//UML:TaggedValue[@modelElement=$classID and @tag='asElement']/@value = 'true')">
			
			<!-- For UML classes of stereotype <<enumeration>>, re-introduce elements back to its XSD counterparts if tagged value asElement = 'true' -->
			<lsx:template xmlns:xs="http://www.w3.org/2001/XMLSchema" match="xs:simpleType[@name='{$className}Type']">

				<lsx:element name="element">
					<lsx:attribute name="name">
						<lsx:value-of select="'{$className}'"/>
					</lsx:attribute>
					<lsx:attribute name="type">
						<lsx:value-of select="'iwxxm:{$className}Type'"/>
					</lsx:attribute>
				</lsx:element>
				<lsx:element name='{{local-name()}}'>
					<lsx:apply-templates select='@*|node()'/>
				</lsx:element>

			</lsx:template>

		</xsl:if>

	</xsl:template>

	<xsl:template match="//UML:Class/UML:ModelElement.taggedValue">

		<xsl:param name="className" select="../@name"/>
		<xsl:param name="classID" select="../@xmi.id"/>
		<xsl:param name="superClassID" select="//UML:Generalization[@subtype=$classID]/@supertype"/>

		<!-- Don't add extension elements to Abstract Classes, Classes with stereotype <<codeList>>, <<enumeration>> and <<union>> and Classes with tagged value noIWXXMExtension="true" -->
		<xsl:if test="not(../@isAbstract = 'true') and not(../UML:ModelElement.stereotype/UML:Stereotype/@name = 'codeList') and not(../UML:ModelElement.stereotype/UML:Stereotype/@name = 'enumeration') and not(../UML:ModelElement.stereotype/UML:Stereotype/@name = 'union') and not(//UML:TaggedValue[@modelElement=$classID and @tag='noIWXXMExtension']/@value = 'true')">

			<!-- To prevent "Unique Particle Attribution" error when a super Class meeting the above criteria is present, the current Class should have at least one non-optional (1) UML attribute without xsdAsAttribute='true' or (2) UML association -->
			<xsl:if test="(count(../UML:Classifier.feature/UML:Attribute/UML:ModelElement.taggedValue/UML:TaggedValue[@tag='lowerBound' and @value!='0']) != count(../UML:Classifier.feature/UML:Attribute/UML:ModelElement.taggedValue/UML:TaggedValue[@tag='lowerBound' and @value!='0']/../UML:TaggedValue[@tag='xsdAsAttribute' and @value='true'])) or exists(//UML:Association/UML:ModelElement.taggedValue/UML:TaggedValue[@tag='ea_sourceName' and @value=$className]/../UML:TaggedValue[@tag='ea_targetName']) or not(exists($superClassID) and not(//UML:Class[@xmi.id=$superClassID]/@isAbstract = 'true') and not(//UML:Class[@xmi.id=$superClassID]/UML:ModelElement.stereotype/UML:Stereotype/@name = 'codeList') and not(//UML:Class[@xmi.id=$superClassID]/UML:ModelElement.stereotype/UML:Stereotype/@name = 'enumeration') and not(//UML:Class[@xmi.id=$superClassID]/UML:ModelElement.stereotype/UML:Stereotype/@name = 'union') and not(//UML:TaggedValue[@modelElement=$superClassID and @tag='noIWXXMExtension']/@value = 'true'))">

				<lsx:template xmlns:xs="http://www.w3.org/2001/XMLSchema" match="xs:complexType[@name='{../@name}Type']//xs:sequence">
					<lsx:element name='{{local-name()}}'>
						<lsx:apply-templates select='@*|node()'/>
						<lsx:element name="element">
							<lsx:attribute name="name">
								<lsx:value-of select="'extension'"/>
							</lsx:attribute>
							<lsx:attribute name="type">
								<lsx:value-of select="'iwxxm:ExtensionType'"/>
							</lsx:attribute>
							<lsx:attribute name="minOccurs">
								<lsx:value-of select="'0'"/>
							</lsx:attribute>
							<lsx:attribute name="maxOccurs">
								<lsx:value-of select="'unbounded'"/>
							</lsx:attribute>
							<lsx:element name="annotation">
								<lsx:element name="documentation">
									<lsx:value-of select="'Extension block for optional and/or additional parameters for element {../@name}'"/>
								</lsx:element>
							</lsx:element>
						</lsx:element>
					</lsx:element>
				</lsx:template>

			</xsl:if>

		</xsl:if>

	</xsl:template>

	<xsl:template match="text()|@*"/>

</xsl:stylesheet>

