############################################################
from vtk import *
import sys
import getopt
############################################################

############################################################
# Global variable for convenience
verbosity = 0
############################################################

############################################################
# Usage function
def Usage( outModelPrefix, outDataName ):
    print "Usage:"
    print "\t -h               Help: print this message and exit"
    print "\t -d <filename>    CSV input data file"
    print "\t -e <engine>      Type of statistics engine. Available engines are:"
    print "\t                    descriptive"
    print "\t                    order"
    print "\t                    contingency"
    print "\t                    correlative"
    print "\t                    multicorrelative"
    print "\t                    pca"
    print "\t                    kmeans"
    print "\t [-m <prefix>]    CSV input model file. Default: calculate model from scratch"
    print "\t [-s <prefix>]    CSV output model (statistics) file prefix. Default:",outModelPrefix
    print "\t [-a <filename>]  CSV output data (annotated) file. Default:",outDataName
    print "\t [-c <filename>]  CSV columns of interest file. Default: all columns are of interest"
    print "\t [-v]             Increase verbosity (0 = silent). Default:",verbosity
    sys.exit( 1 )
############################################################

############################################################
# Parse command line
def ParseCommandLine():
    # Declare use of global variable
    global verbosity

    # Default values
    inModelPrefix = ""
    outModelPrefix = "outputModel"
    outDataName = "outputData.csv"
    columnsListName =""
    
    # Try to hash command line with respect to allowable flags
    try:
        opts,args = getopt.getopt(sys.argv[1:], 'hd:e:m:s:a:c:v')
    except getopt.GetoptError:
        Usage( outModelPrefix, outDataName )
        sys.exit( 1 )

    # First verify that the helper has not been requested (supersedes everything else)
    # NB: handled first and separately so default values cannot be altered in helper message
    for o,a in opts:
        if o == "-h":
            Usage( outModelPrefix, outDataName )

    # Parse arguments and assign corresponding variables
    for o,a in opts:
        if o == "-d":
            inDataName = a
        elif o == "-e":
            haruspexName = a
        elif o == "-m":
            inModelPrefix = a
        elif o == "-s":
            outModelPrefix = a
        elif o == "-a":
            outDataName = a
        elif o == "-c":
            columnsListName = a
        elif o == "-v":
            verbosity += 1

    if not inDataName:
        print "ERROR: a data file name required!"
        sys.exit( 1 )
        
    if not haruspexName:
        print "ERROR: a statistics engine name is required!"
        sys.exit( 1 )

    if verbosity > 0:
        print "# Parsed command line:"

        print "  Input data file:", inDataName
        if inModelPrefix != "":
            print "  Input model file prefix:", inModelPrefix
        else:
            print "  No input model"

        print "  Statistics:", haruspexName
        if columnsListName != "":
            print "  Columns of interest in file:", columnsListName
        else:
            print "  Columns of interest: all"

        print "  Output data file:", outDataName
        print "  Output model file prefix:", outModelPrefix

        print

    return [ inDataName, inModelPrefix, columnsListName, haruspexName, outDataName, outModelPrefix ]
############################################################

############################################################
# Turn haruspex name into vtkStatistics object and ancillary parameters
def InstantiateStatistics( haruspexName ):
    # Declare use of global variable
    global verbosity

    if haruspexName == "descriptive":
        haruspex = vtkDescriptiveStatistics()

    elif haruspexName == "order":
        haruspex = vtkOrderStatistics()

    elif haruspexName == "contingency":
        haruspex = vtkContingencyStatistics()

    elif haruspexName == "correlative":
        haruspex = vtkCorrelativeStatistics()

    elif haruspexName == "multicorrelative":
        haruspex = vtkMultiCorrelativeStatistics()

    elif haruspexName == "pca":
        haruspex = vtkPCAStatistics()

    elif haruspexName == "kmeans":
        haruspex = vtkKMeansStatistics()

    else:
        print "ERROR: Invalid statistics engine:", haruspexName
        sys.exit( 1 )

    if verbosity > 0:
        print "# Instantiated a", haruspex.GetClassName(), "object"
        print

    return haruspex
############################################################

############################################################
# Read input CSV model as input port
def ReadInModel( inModelPrefix ):
    # Declare use of global variable
    global verbosity

    if verbosity > 0:
        print "# Reading input model:"

    # Set CSV reader parameters
    inModelReader = vtkDelimitedTextReader()
    inModelReader.SetFieldDelimiterCharacters(",")
    inModelReader.SetHaveHeaders( True )
    inModelReader.SetDetectNumericColumns( True )
    inModelReader.SetFileName( inModelPrefix + "-0.csv" )
    inModelReader.Update()

    if verbosity > 0:
        table = inModelReader.GetOutput()
        print "  Number of columns:", table.GetNumberOfColumns()
        print "  Number of rows:", table.GetNumberOfRows()
        print
        if verbosity > 1:
            print "# Input Model:"
            inModelReader.GetOutput().Dump( 10 )
            print
    
    return inModelReader
############################################################

############################################################
# Read input CSV data as input port
def ReadInData( inDataName ):
    # Declare use of global variable
    global verbosity

    if verbosity > 0:
        print "# Reading input data:"

    # Set CSV reader parameters
    inDataReader = vtkDelimitedTextReader()
    inDataReader.SetFieldDelimiterCharacters(",")
    inDataReader.SetHaveHeaders( True )
    inDataReader.SetDetectNumericColumns( True )
    inDataReader.SetFileName( inDataName )
    inDataReader.Update()

    if verbosity > 0:
        table = inDataReader.GetOutput()
        print "  Number of columns:", table.GetNumberOfColumns()
        print "  Number of rows:", table.GetNumberOfRows()
        print
        if verbosity > 2:
            print "# Input data:"
            inDataReader.GetOutput().Dump( 10 )
            print
    
    return inDataReader
############################################################

############################################################
# Read list of columns of interest
def ReadColumnsList( columnsListName ):
    # Declare use of global variable
    global verbosity

    if verbosity > 0:
        print "# Reading list of columns of interest:"

    # Set CSV reader parameters
    columnsListReader = vtkDelimitedTextReader()
    columnsListReader.SetFieldDelimiterCharacters(",")
    columnsListReader.SetHaveHeaders( False )
    columnsListReader.SetDetectNumericColumns( True )
    columnsListReader.SetFileName( columnsListName )
    columnsListReader.Update()

    # Figure number of columns of interest
    table = columnsListReader.GetOutput()
    n = table.GetNumberOfColumns()
    if verbosity > 0:
        print "  Number of columns of interest:", n

    # Now construct list of colums of interest
    columnsList = []
    for i in range( 0, n ):
        columnsList.append( table.GetColumn( i ).GetValue( 0 ) )
    if verbosity > 1:
        print "  Columns of interest are:", columnsList

    if verbosity > 0:
        print

    return columnsList
############################################################

############################################################
# Write haruspex output data
def WriteOutData( haruspex, outDataName ):
    # Declare use of global variable
    global verbosity

    if verbosity > 0:
        print "# Saving output (annotated) data:"

    # Set CSV writer parameters
    outDataWriter = vtkDelimitedTextWriter()
    outDataWriter.SetFieldDelimiter(",")
    outDataWriter.SetFileName( outDataName )
    outDataWriter.SetInputConnection( haruspex.GetOutputPort( 0 ) )
    outDataWriter.Update()

    if verbosity > 0:
        print "  Wrote", outDataName
        print
############################################################

############################################################
# Write haruspex output model
def WriteOutModel( haruspex, outModelPrefix ):
    # Declare use of global variable
    global verbosity

    if verbosity > 0:
        print "# Saving output model (statistics):"
        
    # Set CSV writer parameters
    outModelWriter = vtkDelimitedTextWriter()
    outModelWriter.SetFieldDelimiter(",")

    # Get output model type to select appropriate write scheme
    outModelType = haruspex.GetOutputDataObject( 1 ).GetClassName()
    if verbosity > 0:
        print "  Output model is a", outModelType

    # Select write scheme depending on output model type
    if outModelType == "vtkTable":
        # Straightforward CSV file dump of a vtkTable
        outModelName = outModelPrefix + "-0.csv"
        outModelWriter.SetFileName( outModelName )
        outModelWriter.SetInputConnection( haruspex.GetOutputPort( 1 ) )
        outModelWriter.Update()

        if verbosity > 0:
            print "  Wrote", outModelName
            if verbosity > 1:
                haruspex.GetOutput( 1 ).Dump( 10 )

    elif outModelType == "vtkMultiBlockDataSet":
        # Must iterate over all blocks of the vtkMultiBlockDataSet
        outModel = haruspex.GetOutputDataObject( 1 )
        n = outModel.GetNumberOfBlocks()
        for i in range( 0, n ):
            # Straightforward CSV file dump of a vtkTable
            outModelName = outModelPrefix + "-" + str( i )+ ".csv"
            outModelWriter.SetFileName( outModelName )
            table = outModel.GetBlock( i )
            outModelWriter.SetInput( table )
            outModelWriter.Update()
            
            if verbosity > 0:
                print "  Wrote", outModelName
                if verbosity > 1:
                    table.Dump( 10 )

    if verbosity > 0:
        print
############################################################

############################################################
# Calculate statistics
def CalculateStatistics( inDataReader, inModelReader, columnsList, haruspex ):
    # Declare use of global variable
    global verbosity

    if verbosity > 0:
        print "# Calculating statistics:"

    # Output port of data reader becomes input connection of haruspex
    haruspex.AddInputConnection(inDataReader.GetOutputPort() )

    # Get the output table of the data reader, which becomes the input data
    inData = inDataReader.GetOutput()

    # Get the output table of the model reader, which becomes the input model (if available)
    if inModelReader != None:
        inModel = inModelReader.GetOutput()
    else:
        inModel = None

    # Figure number of columns of interest. If no list was provided, use them all
    if columnsList == []:
        columnsList = range( 0, inData.GetNumberOfColumns() )
    n = len( columnsList )
    
    # Generate list of columns of interest, depending on number of variables
    if haruspex.IsA( "vtkUnivariateStatisticsAlgorithm" ):
        # Univariate case: one request for each columns
        for i in range( 0, n ):
            colName = inData.GetColumnName( columnsList[i] )
            if verbosity > 0:
                print "  Requesting column",colName
            haruspex.AddColumn(colName)

    elif haruspex.IsA( "vtkBivariateStatisticsAlgorithm" ):
        # Bivariate case: generate all possible pairs
        for i in range( 0, n ):
            colNameX = inData.GetColumnName( columnsList[i] )
            for j in range( i+1,inData.GetNumberOfColumns() ):
                colNameY = inData.GetColumnName( columnsList[j] )
                if verbosity > 0:
                    print "  Requesting column pair",colNameX,colNameY
                haruspex.AddColumnPair(colNameX,colNameY)

    else:
        # Multivariate case: generate single request containing all columns
        for i in range( 0, n ):
            colName = inData.GetColumnName( columnsList[i] )
            haruspex.SetColumnStatus( colName, 1 )
            if verbosity > 0:
                print "  Adding column", colName, "to the request"

    if verbosity > 0:
        print

    # Complete column selection request
    haruspex.RequestSelectedColumns()
    
    # For now never use the Test option
    haruspex.SetTestOption( False )

    # If an input model was provided, then update it first, otherwise run in a single pass
    if inModel == None:
        # No initial model: then Learn, Derive, and Assess in a single pass
        haruspex.SetLearnOption( True )
        haruspex.SetDeriveOption( True )
        haruspex.SetAssessOption( True )
        haruspex.Update()
    else:
        # There is an initial model: start by storing it for subsequent aggregation
        collection = vtkDataObjectCollection()
        collection.AddItem( inModel )

        # Then learn a new primary model (do not derive nor assess)
        haruspex.SetLearnOption( True )
        haruspex.SetDeriveOption( False )
        haruspex.SetAssessOption( False )
        haruspex.Update()

        # Aggregate old and new models
        collection.AddItem( haruspex.GetOutput( 1 ) )
        aggregated = vtkTable()
        haruspex.Aggregate( collection, aggregated )

        # Finally, derive and assess using the aggregated model (do not learn)
        haruspex.SetInput( 2, aggregated )
        haruspex.SetLearnOption( False )
        haruspex.SetDeriveOption( True )
        haruspex.SetAssessOption( True )
        haruspex.Update()

############################################################

############################################################
# Main function
def main():
    # Parse command line
    [ inDataName, inModelPrefix, columnsListName, haruspexName, outDataName, outModelPrefix ] = ParseCommandLine()

    # Verify that haruspex name makes sense and if so instantiate accordingly
    haruspex = InstantiateStatistics( haruspexName )

    # Set input data reader
    inDataReader = ReadInData( inDataName )

    # Set input model reader if prefix was provided
    if inModelPrefix != "":
        inModelReader = ReadInModel( inModelPrefix )
    else:
        inModelReader = None
        
    # Read list of columns of interest
    if columnsListName:
        columnsList = ReadColumnsList( columnsListName )
    else:
        columnsList = []
        
    # Calculate statistics
    CalculateStatistics( inDataReader, inModelReader, columnsList, haruspex )

    # Save output (annotated) data
    WriteOutData( haruspex, outDataName )

    # Save output model (statistics)
    WriteOutModel( haruspex, outModelPrefix )
############################################################

############################################################
if __name__ == "__main__":
    main()
############################################################
