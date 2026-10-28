# ETAPE 3 : la vue. Elle CHOISIT LE CODE HTTP.
# DRF repond 400 par defaut aux donnees invalides ; notre contrat dit 422.
@api_view(["GET", "POST"])
def acheteurs(request):
    if request.method == "POST":
        serializer = AcheteurSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"message": "Donnees invalides",
                             "errors": serializer.errors}, status=422)
        acheteur = serializer.save()
        return Response(AcheteurSerializer(acheteur).data, status=201)   # cree : 201
    return Response(AcheteurSerializer(Acheteur.objects.all(), many=True).data)


@api_view(["GET", "PUT", "DELETE"])
def acheteur(request, pk):
    obj = get_object_or_404(Acheteur, pk=pk)          # introuvable : 404
    if request.method == "PUT":
        serializer = AcheteurSerializer(obj, data=request.data)
        if not serializer.is_valid():
            return Response({"message": "Donnees invalides",
                             "errors": serializer.errors}, status=422)
        serializer.save()
        return Response(serializer.data)               # modifie : 200
    if request.method == "DELETE":
        obj.delete()
        return Response(status=204)                    # supprime : 204, sans corps
    return Response(AcheteurSerializer(obj).data)
