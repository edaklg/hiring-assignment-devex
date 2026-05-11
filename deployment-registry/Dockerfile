FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY src/DeploymentRegistry.sln .
COPY src/DeploymentRegistry.Api/DeploymentRegistry.Api.csproj DeploymentRegistry.Api/
RUN dotnet restore DeploymentRegistry.Api/DeploymentRegistry.Api.csproj
COPY src/DeploymentRegistry.Api/ DeploymentRegistry.Api/
RUN dotnet publish DeploymentRegistry.Api/DeploymentRegistry.Api.csproj -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .
EXPOSE 8080
ENTRYPOINT ["dotnet", "DeploymentRegistry.Api.dll"]
